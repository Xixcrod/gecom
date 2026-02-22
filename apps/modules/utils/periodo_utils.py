# apps/modules/utils/periodo_utils.py
from apps.core.models import Periodo
from django.core.paginator import Paginator

def obtener_periodos():
    """Consulta y devuelve todos los periodos ordenados del más reciente al más antiguo."""
    return Periodo.objects.all().order_by('-nombre')

def crear_periodo(nombre):
    """Crea y guarda un nuevo periodo en la base de datos."""
    if nombre:
        Periodo.objects.create(nombre=nombre)

def editar_periodo(periodo_id, nuevo_nombre):
    """Busca un periodo por su ID y actualiza su nombre."""
    if periodo_id and nuevo_nombre:
        try:
            periodo = Periodo.objects.get(id=periodo_id)
            periodo.nombre = nuevo_nombre
            periodo.save()
        except Periodo.DoesNotExist:
            pass 

def procesar_formulario_periodo(post_data):
    """Maneja la lógica de decidir si se crea o se edita un periodo basándose en el POST."""
    periodo_id = post_data.get('id')
    nombre_ingresado = post_data.get('nombre')
    
    if periodo_id:
        editar_periodo(periodo_id, nombre_ingresado)
    else:
        crear_periodo(nombre_ingresado)

def obtener_contexto_paginacion(numero_pagina_str, items_por_pagina=16):
    """
    Realiza la paginación y calcula el rango dinámico de 5 páginas (Estilo Carrusel).
    Retorna un diccionario con 'page_obj' y 'custom_page_range' listo para enviarse al template.
    """
    lista_periodos = obtener_periodos()
    paginator = Paginator(lista_periodos, items_por_pagina)
    
    # Validamos que el número de página sea un entero válido
    try:
        numero_pagina = int(numero_pagina_str) if numero_pagina_str else 1
    except ValueError:
        numero_pagina = 1

    page_obj = paginator.get_page(numero_pagina)
    
    # Lógica Matemática para ventana de 5 páginas máximo
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
    
    # Empaquetamos todo en un diccionario
    return {
        'page_obj': page_obj,
        'custom_page_range': custom_page_range
    }