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
    """Maneja la lógica armando la cadena a partir de los 4 selectores."""
    periodo_id = post_data.get('id')
    
    # Capturamos los campos individuales enviados desde el modal
    desde_semestre = post_data.get('desde_semestre')
    desde_anio = post_data.get('desde_anio')
    hasta_semestre = post_data.get('hasta_semestre')
    hasta_anio = post_data.get('hasta_anio')
    
    # Verificamos que todos los campos obligatorios vengan en el POST
    if desde_semestre and desde_anio and hasta_semestre and hasta_anio:
        # Armamos el string final tal como lo espera la base de datos (Ej: "I-2025-II-2025")
        nombre_armado = f"{desde_semestre}-{desde_anio}-{hasta_semestre}-{hasta_anio}"
        
        if periodo_id:
            editar_periodo(periodo_id, nombre_armado)
        else:
            crear_periodo(nombre_armado)

def obtener_contexto_paginacion(numero_pagina_str, items_por_pagina=16):
    """
    Realiza la paginación, rango dinámico y 'desarma' los textos para el modal de edición.
    """
    lista_periodos = obtener_periodos()
    paginator = Paginator(lista_periodos, items_por_pagina)
    
    try:
        numero_pagina = int(numero_pagina_str) if numero_pagina_str else 1
    except ValueError:
        numero_pagina = 1

    page_obj = paginator.get_page(numero_pagina)
    
    # =========================================================================
    # NUEVO: Desarmamos el string guardado para que el HTML pueda pre-seleccionar
    # =========================================================================
    for p in page_obj:
        partes = p.nombre.split('-')
        # Si tiene el formato correcto de 4 partes, las separamos:
        if len(partes) == 4:
            p.desde_semestre = partes[0]
            p.desde_anio = partes[1]
            p.hasta_semestre = partes[2]
            p.hasta_anio = partes[3]
        else:
            # Si hay un dato viejo o mal guardado, le pasamos valores por defecto
            p.desde_semestre = 'I'
            p.desde_anio = ''
            p.hasta_semestre = 'II'
            p.hasta_anio = ''
            
    # Lógica de ventana de 5 páginas
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