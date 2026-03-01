from django.db.models import Q, IntegerField
from django.core.paginator import Paginator
from apps.core.models import Brigada
from django.db.models.functions import Cast # Importa Cast

def obtener_contexto_brigadas(periodo_id, query_search, numero_pagina_str, items_por_pagina=12):
# 1. Filtro base por periodo
    # Usamos annotate para crear una columna temporal 'nombre_int' que sea el nombre convertido a número
    queryset = Brigada.objects.filter(periodo=periodo_id).annotate(
        nombre_int=Cast('nombre', output_field=IntegerField())
    ).order_by('nombre_int') # Ahora ordenamos por esa columna numérica

    # 2. Filtros de búsqueda (Si existen)
    if query_search:
        queryset = queryset.filter(
            Q(nombre__icontains=query_search) | # Por nombre de brigada
            Q(estudiantes__cedula__icontains=query_search) | # Por cédula de estudiante
            Q(asesores__cedula__icontains=query_search) # Por cédula de asesor (vía ManyToMany)
        ).distinct() # Importante: evita duplicados al buscar en relaciones

    # 3. Paginación
    paginator = Paginator(queryset, items_por_pagina)
    
    try:
        numero_pagina = int(numero_pagina_str) if numero_pagina_str else 1
    except ValueError:
        numero_pagina = 1

    page_obj = paginator.get_page(numero_pagina)

    # 4. Rango de páginas (Tu lógica actual optimizada)
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
        'query_search': query_search # Devolvemos el término para mantenerlo en el input
    }