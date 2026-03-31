import os
import re  #Manipipulación complejas de texto mediante patrones expesificos
import uuid
import pypdf #Manipulación y gestión de archivos PDF sin necesidad de software externo
from io import BytesIO #
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from apps.core.models import Proyecto, GrupoDocumentos
from datetime import datetime

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
        print(f"DEBUGGIN ERROR: {e}")
        return False, f"Error interno al procesar el documento."


@login_required
@require_POST # Validación estricta: Solo acepta método POST
def subir_documento_proyecto(request, proyecto_id, tipo_documento):
    '''Vista para subir y validar un documento PDF para un proyecto específico. Y luego guardarlo en el modelo GrupoDocumentos.'''
    # Campos permitidos para evitar inyección de campos en el modelo
    campos_validos = ['planilla_inscripcion', 'control_horas', 'anteproyecto', 'informe_final']
    
    if tipo_documento not in campos_validos:
        return HttpResponseBadRequest("Tipo de documento no reconocido.")

    archivo = request.FILES.get('documento')
    if not archivo:
        return HttpResponseBadRequest("No se adjuntó ningún archivo en la solicitud.")

    # Ejecutar todas las validaciones
    es_valido, resultado = procesar_y_validar_pdf(archivo)
    
    if not es_valido:
        # Si falló, 'resultado' contiene el mensaje de error
        return HttpResponseBadRequest(f"Error de validación: {resultado}")

    # Guardar o actualizar el documento
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    grupo_docs, created = GrupoDocumentos.objects.get_or_create(proyecto=proyecto)
    
    # Asignar el archivo limpio al campo correspondiente dinámicamente
    setattr(grupo_docs, tipo_documento, resultado)
    grupo_docs.save()

    return HttpResponse("Documento subido y validado con éxito.", status=200)


@login_required
@require_POST
def editar_proyecto(request, proyecto_id):
    if request.method == 'POST':
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        # Extraer datos
        nombre_proyecto = request.POST.get('nombre_proyecto', '').strip()
        comunidad = request.POST.get('comunidad', '').strip()
        fecha_inicio_str = request.POST.get('fecha_inicio', '').strip()
        fecha_culminacion_str = request.POST.get('fecha_culminacion', '').strip()
        aprobado_str = request.POST.get('aprobado', 'false').lower()

        # --- VALIDACIONES ---

        # 1. Campos obligatorios
        if not nombre_proyecto or not comunidad or not fecha_inicio_str:
            return JsonResponse({
                'success': False, 
                'error': 'El nombre del proyecto, la comunidad y la fecha de inicio son obligatorios.'
            })

        # 2. Validación y conversión de fechas
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_culminacion = None
            
            if fecha_culminacion_str:
                fecha_culminacion = datetime.strptime(fecha_culminacion_str, '%Y-%m-%d').date()
                
                # Validar coherencia temporal
                if fecha_culminacion < fecha_inicio:
                    return JsonResponse({
                        'success': False, 
                        'error': 'La fecha de culminación no puede ser anterior a la fecha de inicio.'
                    })
        except ValueError:
            return JsonResponse({
                'success': False, 
                'error': 'El formato de las fechas no es válido.'
            })

        # --- ACTUALIZACIÓN ---
        try:
            proyecto.nombre_proyecto = nombre_proyecto
            proyecto.comunidad = comunidad
            proyecto.fecha_inicio = fecha_inicio
            proyecto.fecha_culminacion = fecha_culminacion
            proyecto.aprobado = (aprobado_str == 'true')
            
            proyecto.save()

            return JsonResponse({
                'success': True, 
                'message': '¡Los datos del proyecto se han actualizado exitosamente!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Ocurrió un error al guardar: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'Método no permitido.'})