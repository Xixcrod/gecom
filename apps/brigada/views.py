from django.shortcuts import render
from .utils.brigada_periodo import obtener_contexto_paginacion
from django.contrib.auth.decorators import login_required

# Create your views here.s
@login_required
def brigada_periodo(request):
    '''Vista para mostrar los periodos de brigada con paginación.'''
    numero_pagina = request.GET.get('page')
    context = obtener_contexto_paginacion(numero_pagina)
    return render(request, 'brigada_periodo.html', context)

@login_required
def brigadas(request, periodo_id):
    '''Vista para mostrar las brigadas de un periodo específico.'''
    # Aquí se implementaría la lógica para obtener las brigadas del periodo_id
    # y luego renderizar una plantilla con esa información.
    pass
