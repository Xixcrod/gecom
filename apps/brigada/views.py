from django.shortcuts import render, get_object_or_404
from .utils.brigada_periodo import obtener_contexto_paginacion
from django.contrib.auth.decorators import login_required
from apps.core.models import Periodo, GrupoDocumentos, Brigada, Proyecto
from .utils.brigadas import obtener_contexto_brigadas
from .utils.forms import BrigadaForm
from .utils.brigada_detalles import obtener_contexto_brigada_detalles

# Create your views here.s
@login_required
def brigada_periodo(request):
    '''Vista para mostrar los periodos de brigada con paginación.'''
    numero_pagina = request.GET.get('page')
    context = obtener_contexto_paginacion(numero_pagina)
    return render(request, 'brigada_periodo.html', context)

@login_required
def brigadas(request, periodo_id):
    '''Vista para mostrar las brigadas de un periodo específico, con búsqueda y paginador.'''
    periodo = get_object_or_404(Periodo, id=periodo_id)
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)

    # función auxiliar para obtener la lógica de búsqueda y paginación
    contexto = obtener_contexto_brigadas(periodo_id, query, page)
    
    # Inyectamos el formulario vacío para el modal y los datos del periodo
    contexto.update({
        'periodo': periodo,
        'form': BrigadaForm(),  # Formulario limpio listo para el modal
        'query_search': query,
    })
    
    return render(request, 'brigadas.html', contexto)

@login_required
def brigada_detalles(request, brigada_id):
    '''Vista para mostrar los detalles de una brigada específica.'''
    context = obtener_contexto_brigada_detalles(brigada_id)
    return render(request, 'brigada_detalles.html', context)

@login_required
def proyecto_documentos(request, brigada_id, proyecto_id):
    '''Vista para mostrar los documentos de un proyecto específico dentro de una brigada.'''
    brigada = get_object_or_404(Brigada, id=brigada_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    documents = GrupoDocumentos.objects.filter(proyecto = proyecto).first()  # Obtener el primer grupo de documentos asociado al proyecto
    context = {
        'documents': documents,
        'brigada': brigada,
        'proyecto': proyecto,
    }
    return render(request, 'proyecto_documentos.html', context)