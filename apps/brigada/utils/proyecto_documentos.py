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
from django.contrib import messages
from PIL import Image  #Manipulación de imágenes (JPG, PNG, WEBP)

# Configuraciones
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 * 1024 KB * 1024 Bytes
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

    # 5. Sanear nombre del archivo (Se hace antes para armar el nombre único)
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
            img.verify()  # Verifica que los Magic Bytes realmente correspondan a una imagen
            
            archivo.seek(0)
            img = Image.open(archivo) # Reabrir tras el verify()
            
            # Convertir a RGB si es un formato con transparencia y se guardará como JPEG
            if img.mode in ("RGBA", "P") and ext in ['.jpg', '.jpeg']:
                img = img.convert("RGB")

            img_limpia = BytesIO()
            # Guardar la imagen en memoria (al guardarla desde Pillow, los metadatos EXIF se eliminan por defecto)
            img.save(img_limpia, format=img.format)
            img_limpia.seek(0)
            
            archivo_final = InMemoryUploadedFile(
                file=img_limpia, field_name=nombre_del_campo, name=nombre_unico,
                content_type=archivo.content_type, size=img_limpia.getbuffer().nbytes, charset=None
            )
            return True, archivo_final
        except Exception as e:
            return False, "Error al procesar la imagen. El archivo está corrupto."


@login_required
@require_POST # Validación estricta: Solo acepta método POST
def subir_documento_proyecto(request, proyecto_id, tipo_documento):
    '''Vista para subir y validar un documento PDF para un proyecto específico. Y luego guardarlo en el modelo GrupoDocumentos.'''
    # Campos permitidos para evitar inyección de campos en el modelo
    campos_validos = ['planilla_inscripcion', 'control_horas', 'anteproyecto', 'informe_final', 'constancia_entrega']
    
    if tipo_documento not in campos_validos:
        return JsonResponse({'success': False, 'message': 'Tipo de documento no reconocido.'}, status=400)

    archivo = request.FILES.get('documento')
    if not archivo:
        return JsonResponse({'success': False, 'message': 'No se adjuntó ningún archivo en la solicitud.'}, status=400)

    # Ejecutar todas las validaciones
    es_valido, resultado = procesar_y_validar_pdf(archivo)
    
    if not es_valido:
        # Si falló, 'resultado' contiene el mensaje de error
        return JsonResponse({'success': False, 'message': resultado}, status=400)
    try:
        # Guardar o actualizar el documento
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        grupo_docs, created = GrupoDocumentos.objects.get_or_create(proyecto=proyecto)
        
        # Asignar el archivo limpio al campo correspondiente dinámicamente
        setattr(grupo_docs, tipo_documento, resultado)
        grupo_docs.save()

        messages.success(request, f'Documento "{tipo_documento.replace("_", " ").title()}" subido y validado con éxito.')
        return JsonResponse({'success': True})

    except Exception as e:
        messages.error(request, f"Error interno al guardar el documento: {str(e)}")
        return JsonResponse({'success': False, 'fatal_error': True}, status=500)


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
                'message': 'El nombre del proyecto, la comunidad y la fecha de inicio son obligatorios.'
            }, status=400)

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
                        'message': 'La fecha de culminación no puede ser anterior a la fecha de inicio.'
                    }, status=400)
        except ValueError:
            return JsonResponse({
                'success': False, 
                'message': 'El formato de las fechas no es válido.'
            }, status=400)

        # --- ACTUALIZACIÓN ---
        try:
            proyecto.nombre_proyecto = nombre_proyecto
            proyecto.comunidad = comunidad
            proyecto.fecha_inicio = fecha_inicio
            proyecto.fecha_culminacion = fecha_culminacion
            proyecto.aprobado = (aprobado_str == 'true')
            
            proyecto.save()

            messages.success(request, '¡Los datos del proyecto se han actualizado exitosamente!')
            return JsonResponse({'success': True})
            
        except Exception as e:
            # Error crítico: Usamos mensaje de Django y pedimos recarga
            messages.error(request, f'Error inesperado al guardar: {str(e)}')
            return JsonResponse({'success': False, 'fatal_error': True}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)