# apps/modules/utils/asesor_proyecto_utils.py
from django.contrib import messages
from django.shortcuts import get_object_or_404
from apps.core.models import Proyecto, GrupoDocumentos
from apps.brigada.utils.proyecto_documentos import procesar_y_validar_pdf
import os

def obtener_proyectos_por_asesor_academico(asesor_id):
    """
    Recupera la lista de proyectos en los que participa un asesor académico específico.
    """
    return Proyecto.objects.filter(
        asesor_academico_id=asesor_id
    ).select_related(
        'brigada', 'brigada__periodo'
    ).prefetch_related(
        # PRECARGAMOS LOS ESTUDIANTES PARA EL MODAL SIN GENERAR CONSULTAS EXTRA
        'brigada__estudiantes', 'brigada__estudiantes__carrera'
    ).order_by('-brigada__periodo__nombre') 

def procesar_documento_asesor(request):
    """
    Procesa la subida de la Constancia o el Certificado.
    Reutiliza el escáner de seguridad de PyPDF y guarda el archivo dinámicamente.
    """
    proyecto_id = request.POST.get('proyecto_id')
    tipo_documento = request.POST.get('tipo_documento') # constancia_asesor o certificado_asesor
    archivo = request.FILES.get('documento')

    campos_validos = ['constancia_asesor', 'certificado_asesor']

    if tipo_documento not in campos_validos:
        messages.error(request, "Error: Tipo de documento no reconocido para el asesor.")
        return

    if not archivo:
        messages.error(request, "Error: No se seleccionó ningún archivo.")
        return

    # Escáner de seguridad
    es_valido, resultado = procesar_y_validar_pdf(archivo)
    if not es_valido:
        messages.error(request, f"Error en el archivo: {resultado}")
        return

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    archivo_actual = getattr(proyecto, tipo_documento)

    if archivo_actual:
        # Verificamos si la ruta existe en el almacenamiento para no dar error
        if os.path.isfile(archivo_actual.path):
            try:
                os.remove(archivo_actual.path)
            except Exception as e:
                # Opcional: registrar el error si el archivo está bloqueado o no existe
                print(f"No se pudo borrar el archivo físico: {e}")

    # 5. Guardado del nuevo archivo
    setattr(proyecto, tipo_documento, resultado)
    proyecto.save()

    nombres_legibles = {
        'constancia_asesor': 'Constancia de Asesor',
        'certificado_asesor': 'Certificado de Asesor'
    }
    messages.success(request, f"{nombres_legibles[tipo_documento]} guardada/o exitosamente.")