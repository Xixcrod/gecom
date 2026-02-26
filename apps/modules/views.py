# apps/modules/views.py
from django.shortcuts import render, redirect
from .utils.periodo_utils import procesar_formulario_periodo, obtener_contexto_paginacion
from .utils.carrera_utils import procesar_formulario_carrera, obtener_carreras
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def periodo(request):
    if request.method == 'POST':
        procesar_formulario_periodo(request) 
        return redirect('periodo')
    
    numero_pagina = request.GET.get('page')
    context = obtener_contexto_paginacion(numero_pagina)
    return render(request, 'periodo.html', context)

@login_required
def carrera(request):
    if request.method == 'POST':
        procesar_formulario_carrera(request)
        return redirect('carrera')
    
    context = {
        'carreras': obtener_carreras()
    }
    return render(request, 'carrera.html', context)