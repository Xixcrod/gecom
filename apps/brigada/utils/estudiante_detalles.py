import os
import re  #Manipipulación complejas de texto mediante patrones expesificos
import uuid
import pypdf #Manipulación y gestión de archivos PDF sin necesidad de software externo
from io import BytesIO #
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from apps.core.models import Estudiante, Certificado, Carrera
from django.http import JsonResponse
from django.contrib import messages
from PIL import Image  #Manipulación de imágenes (JPG, PNG, WEBP)

# Configuraciones
MAX_FILE_SIZE = 15 * 1024 * 1024  # 5 * 1024 KB * 1024 Bytes
MAX_FILENAME_LENGTH = 50

def procesar_y_validar_pdf(archivo):
    """
    Valida, sanea y elimina los metadatos de un archivo (PDF o Imagen).
    Retorna: (bool, archivo_limpio_o_mensaje_de_error)
    """
    # 1. Límite de tamaño
    if archivo.size > MAX_FILE_SIZE:
        return False, "El archivo supera el límite de tamaño permitido (15MB)."

    # 2. Límite de longitud del nombre original
    if len(archivo.name) > MAX_FILENAME_LENGTH:
        return False, f"El nombre del archivo excede los {MAX_FILENAME_LENGTH} caracteres."

    # 3. Evitar más de una extensión
    if archivo.name.count('.') > 1:
        return False, "El nombre del archivo no puede contener múltiples puntos/extensiones."

    # 4. Verificar la extensión completa
    ext = os.path.splitext(archivo.name)[1].lower()
    extensiones_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.webp']
    if ext not in extensiones_permitidas:
        return False, "Extensión inválida. Solo se permiten PDF o imágenes (JPG, PNG, WEBP)."

    # 5. Sanear nombre del archivo
    base_name = os.path.splitext(archivo.name)[0]
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', base_name)
    if not clean_name:
        clean_name = "documento"
    
    nombre_unico = f"{clean_name}_{uuid.uuid4().hex[:8]}{ext}"
    nombre_del_campo = getattr(archivo, 'field_name', 'documento')

    # ==========================================
    # LÓGICA PARA ARCHIVOS PDF
    # ==========================================
    if ext == '.pdf':
        if archivo.content_type != 'application/pdf':
            return False, "El Content-Type no corresponde a un PDF."
        
        cabecera = archivo.read(4)
        archivo.seek(0)
        if cabecera != b'%PDF':
            return False, "El archivo está corrupto o no es un PDF válido."

        try:
            reader = pypdf.PdfReader(archivo)
            writer = pypdf.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            writer.add_metadata({}) # Borrar metadatos
            
            pdf_limpio = BytesIO()
            writer.write(pdf_limpio)
            pdf_limpio.seek(0)
            
            archivo_final = InMemoryUploadedFile(
                file=pdf_limpio, field_name=nombre_del_campo, name=nombre_unico,
                content_type='application/pdf', size=pdf_limpio.getbuffer().nbytes, charset=None
            )
            return True, archivo_final
        except Exception:
            return False, "Error al procesar el PDF. Puede estar dañado o encriptado."

    # ==========================================
    # LÓGICA PARA ARCHIVOS DE IMAGEN
    # ==========================================
    else:
        if not archivo.content_type.startswith('image/'):
            return False, "El Content-Type no corresponde a una imagen."
            
        try:
            img = Image.open(archivo)
            img.verify()  # Verifica los Magic Bytes de la imagen
            
            archivo.seek(0)
            img = Image.open(archivo) # Reabrir
            
            # Convertir a RGB si tiene transparencia y se guarda como JPEG
            if img.mode in ("RGBA", "P") and ext in ['.jpg', '.jpeg']:
                img = img.convert("RGB")

            img_limpia = BytesIO()
            img.save(img_limpia, format=img.format) # Al guardar en BytesIO, Pillow limpia los EXIF
            img_limpia.seek(0)
            
            archivo_final = InMemoryUploadedFile(
                file=img_limpia, field_name=nombre_del_campo, name=nombre_unico,
                content_type=archivo.content_type, size=img_limpia.getbuffer().nbytes, charset=None
            )
            return True, archivo_final
        except Exception:
            return False, "Error al procesar la imagen. El archivo está corrupto."


@login_required
@require_POST
def subir_certificado_estudiante(request, estudiante_id):
    '''Vista para subir, validar y actualizar el certificado de un estudiante.'''
    archivo = request.FILES.get('documento')
    if not archivo:
        return JsonResponse({
            'success': False, 
            'message': 'No se adjuntó ningún archivo en la solicitud.'
        }, status=400)
    # procesar_y_validar_pdf
    es_valido, resultado = procesar_y_validar_pdf(archivo)
    
    if not es_valido:
        # Si falló la validación del PDF (tamaño, extensión, corrupto)
        return JsonResponse({'success': False, 'message': resultado}, status=400)
    try:
        # Obtener el estudiante y su certificado asociado
        estudiante = get_object_or_404(Estudiante, id=estudiante_id)
        certificado, created = Certificado.objects.get_or_create(estudiante=estudiante)
        
        # Lógica de asignación de fechas
        if not certificado.archivo_inicial:
            # Si NO hay archivo previo, es la primera vez que se sube
            certificado.archivo_inicial = resultado
            certificado.fecha_entrega = timezone.now().date() 
            mensaje = "Certificado inicial guardado con éxito."
        else:
            # Ya existe el inicial: se guarda/actualiza el segundo campo
            certificado.archivo_actualizado = resultado
            certificado.fecha_actualizacion = timezone.now().date()
            mensaje = "Certificado de actualización guardado con éxito."
        

        certificado.save()
        messages.success(request, mensaje)
        return JsonResponse({'success': True})
    
    except Exception as e:
        # --- ERROR CRÍTICO ---
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
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
                'message': 'Por favor, completa todos los campos obligatorios.'
            }, status=400) # Usamos message y status 400

        # 2. Validar que la cédula no esté en uso por OTRO estudiante
        if Estudiante.objects.filter(cedula=cedula).exclude(id=estudiante.id).exists():
            return JsonResponse({
                'success': False, 
                'message': f'La cédula {cedula} ya está registrada a nombre de otro estudiante.'
            }, status=400)

        # 3. Validar que la carrera exista
        try:
            carrera = Carrera.objects.get(id=carrera_id)
        except Carrera.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'La carrera seleccionada no es válida.'
            }, status=400)

        # --- ACTUALIZACIÓN ---
        
        try:
            estudiante.nombres = nombres
            estudiante.apellidos = apellidos
            estudiante.cedula = cedula
            estudiante.correo = correo
            estudiante.telefono = telefono
            estudiante.carrera = carrera
            estudiante.save()

            # Mensaje de éxito nativo de Django
            messages.success(request, '¡Los datos del estudiante se han actualizado correctamente!')
            return JsonResponse({'success': True})
            
        except Exception as e:
            # Capturar cualquier otro error de base de datos
            # Error crítico para mostrar tras la recarga
            messages.error(request, f'Ocurrió un error interno al guardar: {str(e)}')
            return JsonResponse({'success': False, 'fatal_error': True}, status=500)
    # Si no es POST
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)