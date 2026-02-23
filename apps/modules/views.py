# apps/modules/views.py
from django.shortcuts import render, redirect

# Importamos las utilidades de Periodo
from .utils.periodo_utils import procesar_formulario_periodo, obtener_contexto_paginacion

# Importamos las NUEVAS utilidades de Carrera
from .utils.carrera_utils import procesar_formulario_carrera, obtener_carreras

def index(request):
    return render(request, 'index.html')

# ================= VISTA DE PERIODO =================
def periodo(request):
    if request.method == 'POST':
        procesar_formulario_periodo(request.POST)
        return redirect('periodo')
    
    numero_pagina = request.GET.get('page')
    context = obtener_contexto_paginacion(numero_pagina)
    return render(request, 'periodo.html', context)

# ================= VISTA DE CARRERA =================
def carrera(request):
    # 1. Si enviamos el formulario (Crear o Editar)
    if request.method == 'POST':
        procesar_formulario_carrera(request.POST)
        return redirect('carrera')
    
    # 2. Si entramos a la página normalmente
    context = {
        'carreras': obtener_carreras()
    }
    
    return render(request, 'carrera.html', context)