# apps/modules/utils/carrera_utils.py
import re
from django.contrib import messages
from django.db.models.functions import Lower  # IMPORTANTE: Añadimos esta herramienta
from apps.core.models import Carrera

def validar_nombre_carrera(nombre):
    """Verifica que el nombre contenga letras, espacios, comas o puntos."""
    # Agregamos la coma y el punto (\.) antes de cerrar el corchete
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s,\.]+$'
    return bool(re.match(patron, nombre.strip()))

def obtener_carreras():
    """Consulta y devuelve todas las carreras garantizando el orden alfabético perfecto."""
    # Envolvemos el campo en Lower() para ignorar si el usuario coló una minúscula/mayúscula
    return Carrera.objects.all().order_by(Lower('nombre_carrera'))

def crear_carrera(request, nombre_carrera):
    if nombre_carrera and validar_nombre_carrera(nombre_carrera):
        nombre_limpio = nombre_carrera.strip().title()
        if not Carrera.objects.filter(nombre_carrera__iexact=nombre_limpio).exists():
            Carrera.objects.create(nombre_carrera=nombre_limpio)
            messages.success(request, f"Carrera '{nombre_limpio}' registrada con éxito.")
        else:
            messages.error(request, f"Error: La carrera '{nombre_limpio}' ya está registrada.")
    else:
        messages.error(request, "Error: Nombre inválido. Use solo letras y espacios.")

def editar_carrera(request, carrera_id, nuevo_nombre):
    if carrera_id and nuevo_nombre and validar_nombre_carrera(nuevo_nombre):
        nombre_limpio = nuevo_nombre.strip().title()
        if not Carrera.objects.filter(nombre_carrera__iexact=nombre_limpio).exclude(id=carrera_id).exists():
            try:
                carrera = Carrera.objects.get(id=carrera_id)
                carrera.nombre_carrera = nombre_limpio
                carrera.save()
                messages.success(request, "Carrera actualizada correctamente.")
            except Carrera.DoesNotExist:
                messages.error(request, "Error: La carrera no existe.")
        else:
            messages.error(request, f"Error: El nombre '{nombre_limpio}' ya está en uso.")
    else:
        messages.error(request, "Error: Nombre inválido. Use solo letras y espacios.")

def procesar_formulario_carrera(request):
    carrera_id = request.POST.get('id')
    nombre_ingresado = request.POST.get('nombre_carrera')
    
    if carrera_id:
        editar_carrera(request, carrera_id, nombre_ingresado)
    else:
        crear_carrera(request, nombre_ingresado)