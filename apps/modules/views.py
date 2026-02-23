# apps/modules/views.py
from django.shortcuts import render, redirect

# Importamos solo nuestras dos funciones principales
from .utils.periodo_utils import procesar_formulario_periodo, obtener_contexto_paginacion

def index(request):
    return render(request, 'index.html')

def periodo(request):
    # 1. ¿Recibimos datos del formulario (Crear/Editar)?
    if request.method == 'POST':
        procesar_formulario_periodo(request.POST)
        return redirect('periodo')
    
    # 2. ¿Es una petición normal? Calculamos la página actual
    numero_pagina = request.GET.get('page')
    
    # 3. Delegamos todo el cálculo matemático y de BD a utils
    context = obtener_contexto_paginacion(numero_pagina)
    
    return render(request, 'periodo.html', context)