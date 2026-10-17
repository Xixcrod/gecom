import os
import re
import uuid
from django.core.files.uploadedfile import InMemoryUploadedFile
from apps.core.models import Borrador
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages


def obtener_borradores():
    '''Función para obtener los borradores de la base de datos.'''
    borradores = Borrador.objects.all()
    return {
        'borradores': borradores,
    }

MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB

# Mapeo de categorías con sus extensiones y MIME types permitidos
FORMATOS_PERMITIDOS = {
    'DOCS': {
        'exts': ['.pdf', '.doc', '.docx', '.rtf'],
        'mimes': ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/rtf']
    },
    'DATA': {
        'exts': ['.xls', '.xlsx', '.csv'],
        'mimes': ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']
    },
    'PRES': {
        'exts': ['.ppt', '.pptx'],
        'mimes': ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']
    },
    'IMG': {
        'exts': ['.jpg', '.jpeg', '.png', '.svg'],
        'mimes': ['image/jpeg', 'image/png', 'image/svg+xml']
    },
    'COMP': {
        'exts': ['.zip', '.rar'],
        'mimes': ['application/zip', 'application/x-zip-compressed', 'application/x-rar-compressed']
    }
}


def procesar_y_validar_borrador(archivo, categoria):
    """
    Valida y sanea un archivo genérico basado en su categoría.
    Retorna: (bool, archivo_validado_o_mensaje_error)
    """
    if archivo.size > MAX_FILE_SIZE:
        return False, "El archivo supera el límite de tamaño permitido (30MB)."

    if len(archivo.name) > 50:
        return False, "El nombre del archivo excede los 50 caracteres permitidos."

    if archivo.name.count('.') > 1:
        return False, "El nombre del archivo no puede contener múltiples puntos/extensiones."

    ext = os.path.splitext(archivo.name)[1].lower()
    mime_type = archivo.content_type

    # Validar que la categoría exista
    if categoria not in FORMATOS_PERMITIDOS:
        return False, "La categoría seleccionada no es válida."

    reglas = FORMATOS_PERMITIDOS[categoria]

    # Validar extensión
    if ext not in reglas['exts']:
        return False, f"Extensión inválida para esta categoría. Permitidos: {', '.join(reglas['exts'])}"

    # Validar Content-Type
    if mime_type not in reglas['mimes']:
        return False, "El tipo de archivo (MIME) no coincide con su extensión o está corrupto."

    # Sanitizar el nombre del archivo (solo alfanuméricos y guiones)
    base_name = os.path.splitext(archivo.name)[0]
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', base_name)
    if not clean_name:
        clean_name = "borrador"

    # Generar nombre único para evitar colisiones
    nombre_unico = f"{clean_name}_{uuid.uuid4().hex[:8]}{ext}"
    archivo.name = nombre_unico

    return True, archivo


@login_required
@require_POST
def subir_nuevo_borrador(request):
    '''Vista para manejar la subida de un nuevo borrador desde el modal.'''
    try:
        nombre = request.POST.get('nombre', '').strip()
        categoria = request.POST.get('categoria', '').strip()
        archivo = request.FILES.get('archivo')

        # 1. Validaciones básicas de presencia
        if not nombre or not categoria or not archivo:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'}, status=400)
        
        # 2. Llamar a función validadora
        es_valido, resultado = procesar_y_validar_borrador(archivo, categoria)

        if not es_valido:
            return JsonResponse({'success': False, 'message': resultado}, status=400)

        # 3. Guardar en la Base de Datos
        nuevo_borrador = Borrador(
            nombre=nombre,
            categoria=categoria,
            archivo=resultado  # El archivo validado y con nombre saneado
        )
        nuevo_borrador.save()

        messages.success(request, f'El borrador "{nombre}" se ha subido correctamente.')
        return JsonResponse({'success': True})

    except Exception as e:
        messages.error(request, f'Error crítico: {str(e)}')
        return JsonResponse({
            'success': False, 
            'message': f'Error en el servidor: {str(e)}',
            'fatal_error': True
        }, status=500)

@login_required
@require_POST
def eliminar_borrador(request, uuid_borrador):
    '''Función para eliminar un borrador específico.'''
    try:
        # 1. Buscar el borrador. Si no existe, lanza 404
        borrador = get_object_or_404(Borrador, id=uuid_borrador)
        
        # 2. Eliminar el archivo del almacenamiento remoto (Supabase/S3)
        # borrador.archivo.delete() elimina el objeto del bucket de Supabase.
        # save=False evita que se ejecute una consulta de guardado intermedia en la BD.
        if borrador.archivo:
            borrador.archivo.delete(save=False)
            
        # 3. Eliminar el registro de la base de datos (Neon)
        borrador.delete()
        
        messages.success(request, f'Borrador "{borrador.nombre}" eliminado.') 
        return JsonResponse({'success': True})
        
    except Exception as e:
        messages.error(request, 'No se pudo eliminar el borrador.')
        return JsonResponse({'success': False, 'message': str(e)}, status=500)