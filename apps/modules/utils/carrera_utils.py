# apps/modules/utils/carrera_utils.py
from django.contrib import messages
from apps.core.models import Carrera

def obtener_carreras():
    """Obtiene todas las carreras registradas ordenadas alfabéticamente."""
    return Carrera.objects.all().order_by('nombre_carrera')

def crear_carrera(request, datos):
    """
    Procesa la creación de una nueva carrera.
    Capitaliza la primera letra de cada palabra (Title Case) para mantener consistencia.
    """
    nombre_carrera = datos.get('nombre_carrera', '').strip().title()
    
    if nombre_carrera:
        # Verificamos que no exista una carrera con el mismo nombre exacto
        if Carrera.objects.filter(nombre_carrera=nombre_carrera).exists():
            messages.error(request, "Esta carrera ya existe.")
        else:
            Carrera.objects.create(nombre_carrera=nombre_carrera)
            messages.success(request, "Carrera agregada exitosamente.")

def editar_carrera(request, datos):
    """
    Actualiza el nombre de una carrera existente.
    """
    carrera_id = datos.get('carrera_id')
    nuevo_nombre = datos.get('nombre_carrera', '').strip().title()

    if carrera_id and nuevo_nombre:
        try:
            carrera = Carrera.objects.get(id=carrera_id)
            # Evita registrar nombres duplicados, excluyendo a la carrera actual de la búsqueda
            if Carrera.objects.filter(nombre_carrera=nuevo_nombre).exclude(id=carrera_id).exists():
                messages.error(request, "Ya existe otra carrera con este nombre.")
            else:
                carrera.nombre_carrera = nuevo_nombre
                carrera.save()
                messages.success(request, "Carrera actualizada exitosamente.")
        except Carrera.DoesNotExist:
            messages.error(request, "Error: La carrera no existe.")

def eliminar_carrera(request, datos):
    """
    Elimina permanentemente una carrera del sistema.
    Nota: Al usar CASCADE en los modelos, esto también podría afectar estudiantes vinculados.
    """
    carrera_id = datos.get('carrera_id')
    
    if carrera_id:
        try:
            carrera = Carrera.objects.get(id=carrera_id)
            carrera.delete()
            messages.success(request, "Carrera eliminada exitosamente.")
        except Carrera.DoesNotExist:
            messages.error(request, "Error: La carrera no existe.")

def procesar_formulario_carrera(request):
    """
    Enrutador principal para la vista de Carreras. 
    Llama a la función CRUD correspondiente basándose en el campo oculto 'accion'.
    """
    accion = request.POST.get('accion')
    
    if accion == 'crear':
        crear_carrera(request, request.POST)
    elif accion == 'editar':
        editar_carrera(request, request.POST)
    elif accion == 'eliminar':
        eliminar_carrera(request, request.POST)