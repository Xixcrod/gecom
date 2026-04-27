from django.db.models import Q, IntegerField
from django.core.paginator import Paginator
from apps.core.models import Brigada, Periodo
from django.db.models.functions import Cast  # Importa Cast
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .forms import BrigadaForm
from django.contrib.auth.decorators import login_required


def obtener_contexto_brigadas(periodo_id, query_search, numero_pagina_str, items_por_pagina=16):
    '''Función para obtener el contexto de brigadas con filtros de búsqueda y paginación.'''
    # 1. Filtro base por periodo
    queryset = Brigada.objects.filter(periodo=periodo_id).annotate(
        nombre_int=Cast('nombre', output_field=IntegerField())
    ).order_by('nombre_int')

    # 2. Filtros de búsqueda inteligentes
    if query_search:
        # Siempre buscamos por el nombre de la brigada
        filtros = Q(nombre__icontains=query_search)

        # Solo agregamos la búsqueda por cédula si tiene 7 o más caracteres
        if len(query_search) >= 7:
            filtros |= Q(estudiantes__cedula__icontains=query_search) | \
                Q(asesores__cedula__icontains=query_search)

        queryset = queryset.filter(filtros).distinct()

    # 3. Paginación
    paginator = Paginator(queryset, items_por_pagina)

    try:
        numero_pagina = int(numero_pagina_str) if numero_pagina_str else 1
    except ValueError:
        numero_pagina = 1

    page_obj = paginator.get_page(numero_pagina)

    # 4. Rango de páginas
    current_page = page_obj.number
    total_pages = paginator.num_pages
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)

    if end_page - start_page < 4:
        if start_page == 1:
            end_page = min(total_pages, start_page + 4)
        elif end_page == total_pages:
            start_page = max(1, end_page - 4)

    return {
        'page_obj': page_obj,
        'custom_page_range': range(start_page, end_page + 1),
        'query_search': query_search
    }

@login_required
def crear_brigada(request, periodo_id):
    '''Crea una nueva brigada para un período específico. Si el nombre de la brigada ya existe en ese período, se muestra un mensaje de error.'''
    periodo = get_object_or_404(Periodo, id=periodo_id)

    if request.method == 'POST':
        form = BrigadaForm(request.POST, periodo=periodo)
        if form.is_valid():
            nueva_b = form.save(commit=False)
            nueva_b.periodo = periodo
            nueva_b.save()
            messages.success(
                request, f"Brigada #{form.cleaned_data['nombre']} creada correctamente.")
        else:
            # Si hay errores (como el de duplicado), los pasamos a messages
            for error in form.errors.values():
                messages.error(request, error)

    return redirect('brigadas', periodo_id=periodo.id)
