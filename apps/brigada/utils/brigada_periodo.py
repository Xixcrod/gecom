from apps.core.models import Periodo
from django.core.paginator import Paginator

def sort_periodos_key(periodo):
    """
    Función auxiliar para enseñar a Python a ordenar lógicamente.
    Le da prioridad al año de finalización, luego al semestre final, luego al año inicial.
    """
    partes = periodo.nombre.split('-')
    if len(partes) == 4:
        try:
            desde_sem = partes[0]
            desde_anio = int(partes[1])
            hasta_sem = partes[2]
            hasta_anio = int(partes[3])
            
            # Convertimos números romanos a valores enteros para poder compararlos
            sem_map = {'I': 1, 'II': 2, 'III': 3}
            d_s = sem_map.get(desde_sem, 0) # Traduce el periodo romano a número. Si no encuentra el romano, pone un 0 por seguridad.
            h_s = sem_map.get(hasta_sem, 0)
            
            # Devuelve una tupla de pesos: (2027, 1, 2026, 2)
            return (hasta_anio, h_s, desde_anio, d_s)
        except ValueError:
            pass
    return (0, 0, 0, 0) # Plan B por si hay datos basura

def obtener_periodos():
    """Consulta y devuelve los periodos ordenados cronológicamente desde el más reciente."""
    periodos = list(Periodo.objects.all())
    # reverse=True asegura que los más nuevos (ej. 2027) queden de primeros
    return sorted(periodos, key=sort_periodos_key, reverse=True)

def obtener_contexto_paginacion(numero_pagina_str, items_por_pagina=12):
    lista_periodos = obtener_periodos()
    paginator = Paginator(lista_periodos, items_por_pagina)
    
    try:
        numero_pagina = int(numero_pagina_str) if numero_pagina_str else 1
    except ValueError:
        numero_pagina = 1

    page_obj = paginator.get_page(numero_pagina)
    
    for p in page_obj:
        partes = p.nombre.split('-')
        if len(partes) == 4:
            p.desde_semestre = partes[0]
            p.desde_anio = partes[1]
            p.hasta_semestre = partes[2]
            p.hasta_anio = partes[3]
        else:
            p.desde_semestre = 'I'
            p.desde_anio = ''
            p.hasta_semestre = 'II'
            p.hasta_anio = ''
            
    current_page = page_obj.number
    total_pages = paginator.num_pages
    
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    
    if end_page - start_page < 4:
        if start_page == 1:
            end_page = min(total_pages, start_page + 4)
        elif end_page == total_pages:
            start_page = max(1, end_page - 4)
            
    custom_page_range = range(start_page, end_page + 1)
    
    return {
        'page_obj': page_obj,
        'custom_page_range': custom_page_range
    }