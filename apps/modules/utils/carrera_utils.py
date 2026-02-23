# apps/modules/utils/carrera_utils.py
from apps.core.models import Carrera

def obtener_carreras():
    """Consulta y devuelve todas las carreras ordenadas alfabéticamente."""
    # order_by('nombre_carrera') las ordenará de la A a la Z
    return Carrera.objects.all().order_by('nombre_carrera')

def crear_carrera(nombre_carrera):
    """Crea y guarda una nueva carrera en la base de datos."""
    if nombre_carrera:
        Carrera.objects.create(nombre_carrera=nombre_carrera)

def editar_carrera(carrera_id, nuevo_nombre):
    """Busca una carrera por su ID y actualiza su nombre."""
    if carrera_id and nuevo_nombre:
        try:
            carrera = Carrera.objects.get(id=carrera_id)
            carrera.nombre_carrera = nuevo_nombre
            carrera.save()
        except Carrera.DoesNotExist:
            pass # Si no existe, ignoramos silenciosamente

def procesar_formulario_carrera(post_data):
    """Maneja la lógica de decidir si se crea o se edita una carrera basándose en el POST."""
    carrera_id = post_data.get('id')
    nombre_ingresado = post_data.get('nombre_carrera')
    
    if carrera_id:
        editar_carrera(carrera_id, nombre_ingresado)
    else:
        crear_carrera(nombre_ingresado)