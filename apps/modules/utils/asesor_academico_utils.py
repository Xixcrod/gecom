# apps/modules/utils/asesor_academico_utils.py
import re
from django.contrib import messages
from apps.core.models import Asesor, AsesorAcademico 

def validar_solo_letras(texto):
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
    return bool(re.match(patron, texto.strip()))

def obtener_asesores_academicos():
    return AsesorAcademico.objects.select_related('asesor').order_by('asesor__apellidos', 'asesor__nombres')

def crear_asesor_academico(request, datos):
    nombres = datos.get('nombres', '').strip().title()
    apellidos = datos.get('apellidos', '').strip().title()
    cedula = datos.get('cedula', '').strip() 
    telefono = datos.get('telefono', '').strip().replace('-', '').replace(' ', '')
    correo = datos.get('correo', '').strip().lower()
    
    profesion = datos.get('profesion', '').strip()
    dependencia = datos.get('dependencia', '').strip()
    cargo = datos.get('cargo', '').strip()
    activo = datos.get('estado_activo') == 'True'
    
    if not validar_solo_letras(nombres) or not validar_solo_letras(apellidos):
        messages.error(request, "Error: Nombres y apellidos solo deben contener letras.")
        return
        
    if not cedula.isdigit():
        messages.error(request, "Error: La cédula debe contener únicamente números.")
        return
        
    if not telefono.isdigit():
        messages.error(request, "Error: El teléfono debe contener únicamente números.")
        return
        
    if Asesor.objects.filter(cedula=cedula).exists():
        messages.error(request, f"Error: La cédula {cedula} ya se encuentra registrada.")
        return
        
    nuevo_asesor_base = Asesor.objects.create(
        nombres=nombres, apellidos=apellidos, cedula=cedula, telefono=telefono, correo=correo
    )
    AsesorAcademico.objects.create(
        asesor=nuevo_asesor_base, profesion=profesion, dependencia=dependencia, cargo=cargo, activo=activo 
    )
    messages.success(request, f"Asesor {nombres} {apellidos} registrado exitosamente.")

def editar_asesor_academico(request, datos):
    asesor_id = datos.get('id')
    nombres = datos.get('nombres', '').strip().title()
    apellidos = datos.get('apellidos', '').strip().title()
    cedula = datos.get('cedula', '').strip()
    telefono = datos.get('telefono', '').strip().replace('-', '').replace(' ', '')
    correo = datos.get('correo', '').strip().lower()

    profesion = datos.get('profesion', '').strip()
    dependencia = datos.get('dependencia', '').strip()
    cargo = datos.get('cargo', '').strip()
    activo = datos.get('estado_activo') == 'True'

    if not validar_solo_letras(nombres) or not validar_solo_letras(apellidos):
        messages.error(request, "Error: Nombres y apellidos solo deben contener letras.")
        return
    if not cedula.isdigit() or not telefono.isdigit():
        messages.error(request, "Error: Cédula y teléfono deben contener únicamente números.")
        return

    try:
        # CORRECCIÓN: Buscamos por asesor_id, que es la verdadera clave primaria
        asesor_academico = AsesorAcademico.objects.get(asesor_id=asesor_id)
        asesor_base = asesor_academico.asesor

        if Asesor.objects.filter(cedula=cedula).exclude(id=asesor_base.id).exists():
            messages.error(request, f"Error: La cédula {cedula} ya pertenece a otro asesor.")
            return

        # 1. Actualizamos el modelo base
        asesor_base.nombres = nombres
        asesor_base.apellidos = apellidos
        asesor_base.cedula = cedula
        asesor_base.telefono = telefono
        asesor_base.correo = correo
        asesor_base.save()

        # 2. Actualizamos el modelo académico
        asesor_academico.profesion = profesion
        asesor_academico.dependencia = dependencia
        asesor_academico.cargo = cargo
        asesor_academico.activo = activo
        asesor_academico.save()

        messages.success(request, "Asesor académico actualizado correctamente.")

    except AsesorAcademico.DoesNotExist:
        messages.error(request, "Error: No se pudo encontrar el asesor a editar.")


def cambiar_estado_asesor(request, datos):
    asesor_id = datos.get('id')
    try:
        # CORRECCIÓN: Buscamos por asesor_id aquí también
        asesor = AsesorAcademico.objects.get(asesor_id=asesor_id)
        asesor.activo = not asesor.activo
        asesor.save()
        
        texto_estado = "Habilitado" if asesor.activo else "Deshabilitado"
        messages.success(request, f"El asesor ha sido {texto_estado} exitosamente.")
    except AsesorAcademico.DoesNotExist:
        messages.error(request, "Error: No se encontró el asesor especificado.")


def procesar_formulario_asesor(request):
    """Director de tráfico: Decide qué acción ejecutar según el input oculto del formulario"""
    accion = request.POST.get('accion')
    
    if accion == 'editar':
        editar_asesor_academico(request, request.POST)
    elif accion == 'cambiar_estado':
        cambiar_estado_asesor(request, request.POST)
    else:
        # Por defecto asume crear nuevo
        crear_asesor_academico(request, request.POST)