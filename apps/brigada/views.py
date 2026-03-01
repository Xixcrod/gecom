from django.shortcuts import render, get_object_or_404
from .utils.brigada_periodo import obtener_contexto_paginacion
from django.contrib.auth.decorators import login_required
from apps.core.models import Periodo
from .utils.brigadas import obtener_contexto_brigadas

# Create your views here.s
@login_required
def brigada_periodo(request):
    '''Vista para mostrar los periodos de brigada con paginación.'''
    numero_pagina = request.GET.get('page')
    context = obtener_contexto_paginacion(numero_pagina)
    return render(request, 'brigada_periodo.html', context)

@login_required
def brigadas(request, periodo_id):
    '''Función para mostrar las brigadas de un periodo específico con búsqueda y paginación.'''
    periodo = get_object_or_404(Periodo, id=periodo_id)
    query = request.GET.get('q', '') # Captura el texto del buscador
    page = request.GET.get('page', 1)
    
    contexto = obtener_contexto_brigadas(periodo_id, query, page)
    contexto['periodo'] = periodo # Agregamos el objeto periodo al contexto
    
    return render(request, 'brigadas.html', contexto)