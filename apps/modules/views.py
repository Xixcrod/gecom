# apps/modules/views.py
from django.shortcuts import render, redirect
from .utils.periodo_utils import procesar_formulario_periodo, obtener_contexto_paginacion
from .utils.carrera_utils import procesar_formulario_carrera, obtener_carreras
from .utils.asesor_academico_utils import procesar_formulario_asesor, obtener_asesores_academicos, obtener_asesor_por_id
from .utils.asesor_proyecto_utils import obtener_proyectos_por_asesor_academico, procesar_documento_asesor
from django.contrib.auth.decorators import login_required
from django.urls import reverse

@login_required
def index(request):
    """
    Vista principal de la aplicación.
    Renderiza el dashboard inicial o panel de control para los usuarios autenticados.
    """
    return render(request, 'index.html')

@login_required
def periodo(request):
    """
    Sección en donde se gestionan los periodos académicos.
    """
    if request.method == 'POST':
        procesar_formulario_periodo(request) 
        return redirect('periodo')
    
    numero_pagina = request.GET.get('page')
    context = obtener_contexto_paginacion(numero_pagina)
    return render(request, 'periodo.html', context)

@login_required
def carrera(request):
    """
    Maneja la vista del módulo de Carreras.
    - Procesa peticiones POST (CRUD de carreras) enviándolas al controlador en utils.
    - Pasa la lista completa de carreras al contexto para mostrarlas en la tabla.
    """
    if request.method == 'POST':
        procesar_formulario_carrera(request)
        return redirect('carrera')
    
    context = {
        'carreras': obtener_carreras()
    }
    return render(request, 'carrera.html', context)

@login_required
def asesores_academicos(request):
    """
    Maneja la vista de asesores con soporte para búsqueda y persistencia de pestañas.
    """
    if request.method == 'POST':
        procesar_formulario_asesor(request)
        # Redirigimos manteniendo el estado de búsqueda y pestaña si existen
        query = request.GET.get('q', '')
        tab = request.POST.get('tab_actual', 'activos')
        return redirect(f"{reverse('asesores_academicos')}?q={query}&tab={tab}")
        
    query_search = request.GET.get('q', '')
    tab_actual = request.GET.get('tab', 'activos') # Por defecto 'activos'

    context = {
        'asesores': obtener_asesores_academicos(query_search),
        'query_search': query_search,
        'tab_actual': tab_actual
    }
    
    return render(request, 'asesores_academicos.html', context)

@login_required
def detalle_asesor(request, asesor_id):
    """
    Maneja la vista del Perfil Detallado de un asesor específico.
    """
    # ====== AGREGAR ESTE BLOQUE POST ======
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'subir_doc_asesor':
            procesar_documento_asesor(request)
            return redirect('detalle_asesor', asesor_id=asesor_id)
    # ======================================

    context = {
        'asesor': obtener_asesor_por_id(asesor_id),
        'proyectos': obtener_proyectos_por_asesor_academico(asesor_id)
    }
    return render(request, 'detalle_asesor.html', context)