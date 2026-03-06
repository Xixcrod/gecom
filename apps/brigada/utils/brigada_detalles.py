from django.shortcuts import get_object_or_404
from apps.core.models import Brigada, AsesorAcademico, AsesorComunitario, BrigadaAsesor, Asesor, Periodo
from django.http import JsonResponse
import json
from django.contrib import messages
from django.shortcuts import redirect
from .forms import BrigadaForm

def obtener_contexto_brigada_detalles(brigada_id):
    '''Obtiene el contexto necesario para la vista de detalles de una brigada, incluyendo información sobre la brigada, su proyecto asociado, estudiantes y asesores.'''
    brigada = get_object_or_404(
        Brigada.objects.select_related('periodo').prefetch_related('estudiantes__carrera'),
        id=brigada_id
    )
    proyecto = brigada.proyectos.first()

    # Buscamos los enlaces en BrigadaAsesor
    academico_link = brigada.brigadaasesor_set.filter(rol='ACADEMICO').first()
    comunitario_link = brigada.brigadaasesor_set.filter(rol='COMUNITARIO').first()

    # Extraemos la instancia hija correspondiente si existe
    asesor_academico = None
    if academico_link and hasattr(academico_link.asesor, 'asesoracademico'):
        asesor_academico = academico_link.asesor.asesoracademico

    asesor_comunitario = None
    if comunitario_link and hasattr(comunitario_link.asesor, 'asesorcomunitario'):
        asesor_comunitario = comunitario_link.asesor.asesorcomunitario

    # Lista de académicos activos para el selector
    academicos_activos = AsesorAcademico.objects.filter(activo=True).select_related('asesor')

    return {
        'brigada': brigada,
        'proyecto': proyecto,
        'estudiantes': brigada.estudiantes.all(),
        'asesor_academico': asesor_academico,
        'asesor_comunitario': asesor_comunitario,
        'academicos_activos': academicos_activos,
    }

def guardar_asesor_comunitario(request, brigada_id):
    '''Guarda o actualiza un asesor comunitario para una brigada específica. Si se proporciona un ID de asesor, se actualiza; de lo contrario, se crea uno nuevo y se asigna a la brigada.'''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            brigada = Brigada.objects.get(id=brigada_id)
            asesor_id = data.get('asesor_id')

            if asesor_id:
                # Modificar existente
                asesor = Asesor.objects.get(id=asesor_id)
                asesor.nombres = data['nombres']
                asesor.apellidos = data['apellidos']
                asesor.cedula = data['cedula']
                asesor.telefono = data['telefono']
                asesor.correo = data['correo']
                asesor.save()
                mensaje = "Asesor comunitario actualizado con éxito."
            else:
                # Crear nuevo
                nuevo_asesor = Asesor.objects.create(
                    nombres=data['nombres'],
                    apellidos=data['apellidos'],
                    cedula=data['cedula'],
                    telefono=data['telefono'],
                    correo=data['correo']
                )
                AsesorComunitario.objects.create(asesor=nuevo_asesor)
                BrigadaAsesor.objects.create(brigada=brigada, asesor=nuevo_asesor, rol='COMUNITARIO')
                mensaje = "Asesor comunitario creado y asignado."

            return JsonResponse({'success': True, 'message': mensaje})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

def asignar_asesor_academico(request, brigada_id):
    '''Asigna un asesor académico a una brigada específica.'''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            brigada = Brigada.objects.get(id=brigada_id)
            asesor_base_id = data.get('asesor_base_id') # ID del modelo Asesor base

            asesor_base = Asesor.objects.get(id=asesor_base_id)
            
            # Buscamos si ya tiene uno asignado y lo actualizamos, o creamos uno nuevo
            link, created = BrigadaAsesor.objects.update_or_create(
                brigada=brigada,
                rol='ACADEMICO',
                defaults={'asesor': asesor_base}
            )
            return JsonResponse({'success': True, 'message': 'Asesor académico asignado con éxito.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})