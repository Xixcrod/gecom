# apps/modules/utils/asesor_proyecto_utils.py
from apps.core.models import Proyecto

def obtener_proyectos_por_asesor_academico(asesor_id):
    """
    Recupera la lista de proyectos en los que participa un asesor académico específico.
    
    Parámetros:
    - asesor_id: UUID del modelo base (Asesor) que actúa como llave primaria del AsesorAcademico.
    
    Retorna:
    - QuerySet de Proyectos ordenados de forma descendente por periodo.
    """
    # Filtramos directamente por el campo ForeignKey 'asesor_academico' del modelo Proyecto.
    # Usamos select_related para precargar los datos de la Brigada y el Periodo,
    # permitiendo acceder a proyecto.brigada.periodo.nombre en el HTML sin generar consultas extra.
    proyectos = Proyecto.objects.filter(
        asesor_academico_id=asesor_id
    ).select_related(
        'brigada', 'brigada__periodo'
    ).order_by('-brigada__periodo__nombre') 
    
    return proyectos