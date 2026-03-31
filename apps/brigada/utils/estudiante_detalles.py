import os
import re  #Manipipulación complejas de texto mediante patrones expesificos
import uuid
import pypdf #Manipulación y gestión de archivos PDF sin necesidad de software externo
from io import BytesIO #
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from apps.core.models import Estudiante, Certificado, Carrera
from django.http import JsonResponse

# Configuraciones
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 * 1024 KB * 1024 Bytes
MAX_FILENAME_LENGTH = 50

def procesar_y_validar_pdf(archivo):
    """
    Valida, sanea y elimina los metadatos de un archivo PDF.
    Retorna: (bool, archivo_limpio_o_mensaje_de_error)
    """
    # 1. Límite de tamaño
    if archivo.size > MAX_FILE_SIZE:
        return False, "El archivo supera el límite de tamaño permitido (5MB)."

    # 2. Límite de longitud del nombre original
    if len(archivo.name) > MAX_FILENAME_LENGTH:
        return False, f"El nombre del archivo excede los {MAX_FILENAME_LENGTH} caracteres."

    # 3. Evitar más de una extensión (ej. archivo.php.pdf)
    if archivo.name.count('.') > 1:
        return False, "El nombre del archivo no puede contener múltiples puntos/extensiones."

    # 4. Verificar la extensión completa
    #Obteniendo la extensión del archivo separando el nombre del archivo por el punto y tomando la parte final, luego se convierte a minúscula para evitar problemas de mayúsculas/minúsculas.
    #['archivo', 'pdf'] -> 'pdf'
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext != '.pdf':
        return False, "Extensión inválida. Solo se permiten archivos .pdf."

    # 5. Evaluar Content-Type y Magic Bytes (Cabecera real del archivo)
    if archivo.content_type != 'application/pdf':
        return False, "El Content-Type no corresponde a un PDF."
    
    # Leer los primeros bytes para verificar la cabecera PDF (Magic Bytes) y asegurarnos de que el archivo no esté corrupto
    cabecera = archivo.read(4)
    archivo.seek(0) # Regresar el puntero al inicio
    if cabecera != b'%PDF':
        return False, "El archivo está corrupto o no es un PDF válido."

    # 6. Evitar caracteres neutros/peligrosos (Sanitización del nombre)
    base_name = os.path.splitext(archivo.name)[0]
    # Solo permitimos letras, números, guiones y guiones bajos
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', base_name)
    if not clean_name:
        clean_name = "documento"

    # 7. Evitar sobreescritura (Generar nombre único con UUID)
    nombre_unico = f"{clean_name}_{uuid.uuid4().hex[:8]}.pdf"

    # 8. Borrar metadatos reescribiendo el PDF
    try:
        reader = pypdf.PdfReader(archivo)
        writer = pypdf.PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        # Inyectar un diccionario de metadatos vacío
        writer.add_metadata({})
        
        # Guardar en memoria
        pdf_limpio = BytesIO()
        writer.write(pdf_limpio)
        pdf_limpio.seek(0)
        
        tamano_nuevo = pdf_limpio.getbuffer().nbytes
        nombre_del_campo = getattr(archivo, 'field_name', 'documento')
        
        # Crear un nuevo objeto de archivo de Django
        archivo_final = InMemoryUploadedFile(
            file=pdf_limpio,
            field_name=nombre_del_campo,
            name=nombre_unico,
            content_type='application/pdf',
            size=tamano_nuevo,
            charset=None
        )
        return True, archivo_final

    except pypdf.errors.PdfReadError:
        return False, "No se pudo leer el PDF. Puede estar encriptado o dañado."
    except Exception as e:
        return False, f"Error interno al procesar el documento."


@login_required
@require_POST
def subir_certificado_estudiante(request, estudiante_id):
    '''Vista para subir, validar y actualizar el certificado de un estudiante.'''
    archivo = request.FILES.get('documento')
    if not archivo:
        return HttpResponseBadRequest("No se adjuntó ningún archivo en la solicitud.")

    # Reutilizamos tu función procesar_y_validar_pdf
    es_valido, resultado = procesar_y_validar_pdf(archivo)
    
    if not es_valido:
        return HttpResponseBadRequest(f"Error de validación: {resultado}")

    # Obtener el estudiante y su certificado asociado
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    certificado, created = Certificado.objects.get_or_create(estudiante=estudiante)
    
    # Lógica de asignación de fechas
    if not certificado.archivo:
        # Si NO hay archivo previo, es la primera vez que se sube
        certificado.fecha_retiro = timezone.now().date() # Usa .date() o timezone.now() según tu modelo
    else:
        # Si YA existe un archivo, se está modificando
        certificado.fecha_actualizacion = timezone.now().date()
    
    # Guardar el documento limpio procesado por pypdf
    certificado.archivo = resultado
    certificado.save()

    return HttpResponse("Certificado procesado y guardado con éxito.", status=200)

def editar_estudiante(request, estudiante_id):
    # Verificar que la petición sea AJAX y sea POST
    if request.method == 'POST':
        estudiante = get_object_or_404(Estudiante, id=estudiante_id)

        # Extraer los datos del formulario y limpiar espacios en blanco
        nombres = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        carrera_id = request.POST.get('carrera_id', '').strip()

        # --- VALIDACIONES ---

        # 1. Validar que no haya campos vacíos
        if not all([nombres, apellidos, cedula, correo, telefono, carrera_id]):
            return JsonResponse({
                'success': False, 
                'error': 'Por favor, completa todos los campos obligatorios.'
            })

        # 2. Validar que la cédula no esté en uso por OTRO estudiante
        if Estudiante.objects.filter(cedula=cedula).exclude(id=estudiante.id).exists():
            return JsonResponse({
                'success': False, 
                'error': f'La cédula {cedula} ya está registrada a nombre de otro estudiante.'
            })

        # 3. Validar que la carrera exista
        try:
            carrera = Carrera.objects.get(id=carrera_id)
        except Carrera.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'La carrera seleccionada no es válida.'
            })

        # --- ACTUALIZACIÓN ---
        
        try:
            estudiante.nombres = nombres
            estudiante.apellidos = apellidos
            estudiante.cedula = cedula
            estudiante.correo = correo
            estudiante.telefono = telefono
            estudiante.carrera = carrera
            estudiante.save()

            return JsonResponse({
                'success': True, 
                'message': '¡Datos actualizados correctamente!'
            })
            
        except Exception as e:
            # Capturar cualquier otro error de base de datos
            return JsonResponse({
                'success': False, 
                'error': f'Ocurrió un error interno al guardar: {str(e)}'
            })

    # Si no es POST
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})