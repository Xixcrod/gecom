from django.shortcuts import render, get_object_or_404, redirect
from .utils.brigada_periodo import obtener_contexto_paginacion
from django.contrib.auth.decorators import login_required
from apps.core.models import Periodo, Brigada
from .utils.brigadas import obtener_contexto_brigadas
from django.contrib import messages
from .utils.forms import BrigadaForm

# Create your views here.s
@login_required
def brigada_periodo(request):
    '''Vista para mostrar los periodos de brigada con paginación.'''
    numero_pagina = request.GET.get('page')
    context = obtener_contexto_paginacion(numero_pagina)
    return render(request, 'brigada_periodo.html', context)

@login_required
def brigadas(request, periodo_id):
    '''Vista para mostrar las brigadas de un periodo específico, con búsqueda, paginador y creación de nuevas brigadas.'''
    periodo = get_object_or_404(Periodo, id=periodo_id)
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    
    # Manejo del Formulario Modal (POST)
    form = BrigadaForm()
    if request.method == 'POST':
        form = BrigadaForm(request.POST)
        if form.is_valid():
            nombre_nuevo = form.cleaned_data['nombre']
            # Validación de existencia en el periodo actual
            if Brigada.objects.filter(periodo=periodo, nombre=nombre_nuevo).exists():
                messages.error(request, f"La Brigada #{nombre_nuevo} ya existe en este periodo.")
            else:
                nueva_b = form.save(commit=False)
                nueva_b.periodo = periodo
                nueva_b.save()
                messages.success(request, f"Brigada #{nombre_nuevo} creada correctamente.")
                return redirect('brigadas', periodo_id=periodo.id)

    # Lógica original de contexto
    contexto = obtener_contexto_brigadas(periodo_id, query, page)
    contexto.update({
        'periodo': periodo,
        'form': form,
        'query_search': query,
    })
    
    return render(request, 'brigadas.html', contexto)