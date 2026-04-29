# apps/modules/utils/carrera_utils.py
import os
import re
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db.models.functions import Lower
from apps.core.models import Carrera


def validar_nombre_carrera(nombre):
    """Verifica que el nombre contenga letras, espacios, comas o puntos."""
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s,\.]+$'
    return bool(re.match(patron, nombre.strip()))


def validar_icono_carrera(archivo):
    """Valida el peso y el formato antes de procesar la imagen."""
    if not archivo:
        return True, ""

    limite_mb = 2
    if archivo.size > limite_mb * 1024 * 1024:
        return False, f"La imagen excede el límite de {limite_mb}MB."

    ext_validas = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in ext_validas:
        return False, "Formato no permitido. Solo imágenes (JPG, PNG, WEBP)."

    tipos_validos = ['image/jpeg', 'image/png', 'image/webp']
    if archivo.content_type not in tipos_validos:
        return False, "El archivo corrupto o no es una imagen válida."

    return True, ""


def optimizar_imagen_carrera(archivo):
    """
    Toma la imagen subida y la redimensiona para que encaje perfectamente 
    sin recortar ninguna parte (manteniendo su proporción original).
    """
    if not archivo:
        return None

    try:
        # Abrimos la imagen con Pillow
        img = Image.open(archivo)

        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA')

        # Definimos el tamaño máximo del contenedor de la tarjeta
        tamano_ideal = (800, 600)

        # ImageOps.contain escala la imagen (agrandando o achicando) para que
        # quepa exactamente dentro del tamaño ideal, SIN recortar nada.
        img_optimizada = ImageOps.contain(
            img, tamano_ideal, Image.Resampling.LANCZOS)

        # Guardamos la imagen temporalmente en memoria RAM.
        # USAMOS WEBP: Es vital porque a diferencia del JPEG, el WEBP soporta
        # transparencia. Si se sube un logo sin fondo, no se le pondrá un fondo negro.
        buffer = BytesIO()
        img_optimizada.save(buffer, format='WEBP', quality=85)

        # Renombramos el archivo a .webp
        nombre_base = os.path.splitext(archivo.name)[0]
        nuevo_nombre = f"{nombre_base}_opt.webp"

        return ContentFile(buffer.getvalue(), name=nuevo_nombre)
    except Exception as e:
        # Fallback de seguridad: si falla, devuelve la original
        return archivo


def obtener_carreras():
    return Carrera.objects.all().order_by(Lower('nombre_carrera'))


def crear_carrera(request):
    nombre_carrera = request.POST.get('nombre_carrera', '')
    icono_original = request.FILES.get('icono')

    if nombre_carrera and validar_nombre_carrera(nombre_carrera):
        nombre_limpio = nombre_carrera.strip().title()

        imagen_valida, msj_error = validar_icono_carrera(icono_original)
        if not imagen_valida:
            messages.error(request, msj_error)
            return

        if not Carrera.objects.filter(nombre_carrera__iexact=nombre_limpio).exists():
            icono_final = optimizar_imagen_carrera(
                icono_original) if icono_original else None
            Carrera.objects.create(
                nombre_carrera=nombre_limpio, icono=icono_final)
            messages.success(
                request, f"Carrera '{nombre_limpio}' registrada con éxito.")
        else:
            messages.error(
                request, f"Error: La carrera '{nombre_limpio}' ya está registrada.")
    else:
        messages.error(
            request, "Error: Nombre inválido. Use solo letras y espacios.")


def editar_carrera(request):
    carrera_id = request.POST.get('carrera_id')
    nuevo_nombre = request.POST.get('nombre_carrera', '')
    icono_original = request.FILES.get('icono')

    if carrera_id and nuevo_nombre and validar_nombre_carrera(nuevo_nombre):
        nombre_limpio = nuevo_nombre.strip().title()

        if icono_original:
            imagen_valida, msj_error = validar_icono_carrera(icono_original)
            if not imagen_valida:
                messages.error(request, msj_error)
                return

        if not Carrera.objects.filter(nombre_carrera__iexact=nombre_limpio).exclude(id=carrera_id).exists():
            try:
                carrera = Carrera.objects.get(id=carrera_id)
                carrera.nombre_carrera = nombre_limpio
                if icono_original:
                    if carrera.icono and os.path.isfile(carrera.icono.path):
                        os.remove(carrera.icono.path)
                    carrera.icono = optimizar_imagen_carrera(icono_original)
                carrera.save()
                messages.success(request, "Carrera actualizada exitosamente.")
            except Carrera.DoesNotExist:
                messages.error(request, "Error: La carrera no existe.")
        else:
            messages.error(
                request, f"Error: El nombre '{nombre_limpio}' ya está en uso.")
    else:
        messages.error(
            request, "Error: Nombre inválido. Use solo letras y espacios.")


def procesar_formulario_carrera(request):
    accion = request.POST.get('accion')
    if accion == 'crear':
        crear_carrera(request)
    elif accion == 'editar':
        editar_carrera(request)
