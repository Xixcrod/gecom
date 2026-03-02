# apps/modules/views.py
from django.shortcuts import render, redirect
from .utils.periodo_utils import procesar_formulario_periodo, obtener_contexto_paginacion
from .utils.carrera_utils import procesar_formulario_carrera, obtener_carreras
from .utils.asesor_academico_utils import procesar_formulario_asesor, obtener_asesores_academicos, obtener_asesor_por_id
from .utils.asesor_proyecto_utils import obtener_proyectos_por_asesor_academico
from django.contrib.auth.decorators import login_required

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
    Maneja la vista del módulo de Periodos Académicos.
    - Si la petición es POST: Delega la lógica de creación, edición o eliminación al archivo utils y recarga.
    - Si la petición es GET: Carga el contexto paginado y renderiza la lista de periodos.
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
    Maneja la vista general del directorio de Asesores Académicos.
    Recibe las peticiones de los formularios modales (Añadir, Editar, Deshabilitar)
    y carga la lista completa de asesores activos e inactivos.
    """
    if request.method == 'POST':
        procesar_formulario_asesor(request)
        return redirect('asesores_academicos')
        
    # Pasamos la lista de asesores al contexto para usarla luego en la tabla/grid
    context = {
        'asesores': obtener_asesores_academicos()
    }
    
    return render(request, 'asesores_academicos.html', context)

@login_required
def detalle_asesor(request, asesor_id):
    """
    Maneja la vista del Perfil Detallado de un asesor específico.
    Recibe el UUID del asesor a través de la URL (asesor_id).
    Consulta su información base y busca de forma relacional todos los proyectos
    de servicio comunitario a los que este asesor está vinculado.
    """
    context = {
        'asesor': obtener_asesor_por_id(asesor_id),
        'proyectos': obtener_proyectos_por_asesor_academico(asesor_id)
    }
    return render(request, 'detalle_asesor.html', context)