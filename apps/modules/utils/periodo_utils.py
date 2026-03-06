# apps/modules/utils/periodo_utils.py
from apps.core.models import Periodo
from django.core.paginator import Paginator
from django.contrib import messages

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
            d_s = sem_map.get(desde_sem, 0)
            h_s = sem_map.get(hasta_sem, 0)
            
            # Devuelve una tupla de pesos: (2027, 1, 2026, 2)
            # Python usará esta tupla para determinar el orden exacto
            return (hasta_anio, h_s, desde_anio, d_s)
        except ValueError:
            pass
    return (0, 0, 0, 0) # Fallback por si hay datos basura

def obtener_periodos():
    """Consulta y devuelve los periodos ordenados cronológicamente desde el más reciente."""
    periodos = list(Periodo.objects.all())
    # reverse=True asegura que los más nuevos (ej. 2027) queden de primeros
    return sorted(periodos, key=sort_periodos_key, reverse=True)

def crear_periodo(nombre):
    """Crea y guarda un nuevo registro de Periodo en la base de datos."""
    if nombre:
        Periodo.objects.create(nombre=nombre)

def editar_periodo(periodo_id, nuevo_nombre):
    """
    Actualiza el nombre de un periodo existente buscándolo por su ID.
    Maneja silenciosamente la excepción si el periodo no existe.
    """
    if periodo_id and nuevo_nombre:
        try:
            periodo = Periodo.objects.get(id=periodo_id)
            periodo.nombre = nuevo_nombre
            periodo.save()
        except Periodo.DoesNotExist:
            pass 

def procesar_formulario_periodo(request):
    """
    Procesa los datos enviados desde el formulario (POST).
    Se encarga de armar el nombre del periodo, validar que las fechas tengan sentido 
    cronológico y delegar la acción a crear_periodo o editar_periodo según corresponda.
    """
    periodo_id = request.POST.get('id')
    desde_semestre = request.POST.get('desde_semestre')
    desde_anio = request.POST.get('desde_anio')
    hasta_semestre = request.POST.get('hasta_semestre')
    hasta_anio = request.POST.get('hasta_anio')
    
    if desde_semestre and desde_anio and hasta_semestre and hasta_anio:
        try:
            d_anio = int(desde_anio)
            h_anio = int(hasta_anio)
            
            if 2000 <= d_anio <= 2100 and 2000 <= h_anio <= 2100:
                # Validar incongruencias temporales (Ej: Inicia en 2025 y termina en 2024)
                if d_anio > h_anio:
                    messages.error(request, "Error: El año de inicio no puede ser mayor al de finalización.")
                    return
                
                # Validar incongruencias semestrales en el mismo año
                if d_anio == h_anio and desde_semestre in ['II', 'III'] and hasta_semestre == 'I':
                    messages.error(request, "Error: El semestre final no puede ocurrir antes que el inicial.")
                    return
                if d_anio == h_anio and desde_semestre == 'III' and hasta_semestre == 'II':
                    messages.error(request, "Error: El semestre final no puede ocurrir antes que el inicial.")
                    return
                
                # Ensambla el string final (Ej: 'I-2024-II-2024')
                nombre_armado = f"{desde_semestre}-{d_anio}-{hasta_semestre}-{h_anio}"
                
                # Flujo de Edición
                if periodo_id:
                    # Verifica que el nuevo nombre no choque con otro periodo ya existente
                    if not Periodo.objects.filter(nombre=nombre_armado).exclude(id=periodo_id).exists():
                        editar_periodo(periodo_id, nombre_armado)
                        messages.success(request, "Periodo actualizado exitosamente.")
                    else:
                        messages.error(request, "Error: Este periodo ya se encuentra registrado.")
                # Flujo de Creación
                else:
                    if not Periodo.objects.filter(nombre=nombre_armado).exists():
                        crear_periodo(nombre_armado)
                        messages.success(request, "Periodo creado exitosamente.")
                    else:
                        messages.error(request, "Error: Este periodo ya se encuentra registrado.")
            else:
                messages.error(request, "Error: Los años deben estar entre 2000 y 2100.")
                        
        except ValueError:
            messages.error(request, "Error: Datos numéricos inválidos.")

def obtener_contexto_paginacion(numero_pagina_str, items_por_pagina=16):
    """
    Prepara los datos paginados y calcula el rango visible de los botones de paginación.
    Además, inyecta atributos temporales a cada objeto Periodo para facilitar
    su renderizado en el formulario del frontend.
    """
    lista_periodos = obtener_periodos()
    paginator = Paginator(lista_periodos, items_por_pagina)
    
    try:
        numero_pagina = int(numero_pagina_str) if numero_pagina_str else 1
    except ValueError:
        numero_pagina = 1

    page_obj = paginator.get_page(numero_pagina)
    
    # Descompone el nombre de cada periodo de la página actual 
    # en sus 4 partes para usarlas directamente en los inputs del HTML
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
            
    # Lógica matemática para crear la "ventana" de botones de paginación (Ej: [1] [2] [3] 4 5)
    current_page = page_obj.number
    total_pages = paginator.num_pages
    
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    
    # Ajusta la ventana si estamos en los extremos (al principio o al final)
    if end_page - start_page < 4:
        if start_page == 1:
            end_page = min(total_pages, start_page + 4)
        elif end_page == total_pages:
            start_page = max(1, end_page - 4)
            
    custom_page_range = range(start_page, end_page + 1)
    
    # Retorna un diccionario listo para ser inyectado en el context de la vista
    return {
        'page_obj': page_obj,
        'custom_page_range': custom_page_range
    }