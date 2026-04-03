# apps/modules/utils/asesor_academico_utils.py
import re
from django.contrib import messages
from django.db.models import Q
from apps.core.models import Asesor, AsesorAcademico 
from django.shortcuts import get_object_or_404

def validar_solo_letras(texto):
    """
    Verifica que el texto ingresado contenga únicamente letras (incluyendo acentos y ñ) y espacios.
    Retorna True si el texto es válido, False en caso contrario.
    """
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
    return bool(re.match(patron, texto.strip()))

def obtener_asesores_academicos(query_search=None):
    """
    Obtiene los asesores con soporte para búsqueda por nombre, apellido o cédula.
    """
    queryset = AsesorAcademico.objects.select_related('asesor').order_by('asesor__apellidos', 'asesor__nombres')
    
    if query_search:
        # Filtramos por nombres, apellidos o cédula (usando la relación con el modelo padre Asesor)
        filtros =   Q(asesor__nombres__icontains=query_search) | \
                    Q(asesor__apellidos__icontains=query_search) | \
                    Q(asesor__cedula__icontains=query_search)
        
        queryset = queryset.filter(filtros).distinct()
        
    return queryset

def obtener_asesor_por_id(asesor_id):
    """Busca un asesor específico, si no existe devuelve error 404 de forma segura."""
    return get_object_or_404(AsesorAcademico.objects.select_related('asesor'), asesor_id=asesor_id)

def crear_asesor_academico(request, datos):
    """
    Procesa la creación de un nuevo Asesor Académico.
    Extrae, limpia y valida los datos. Debido a la herencia de modelos, 
    primero crea el registro en la tabla base (Asesor) y luego el registro vinculado (AsesorAcademico).
    """
    nombres = datos.get('nombres', '').strip().title()
    apellidos = datos.get('apellidos', '').strip().title()
    cedula = datos.get('cedula', '').strip() 
    telefono = datos.get('telefono', '').strip().replace('-', '').replace(' ', '')
    correo = datos.get('correo', '').strip().lower()
    
    profesion = datos.get('profesion', '').strip()
    dependencia = datos.get('dependencia', '').strip()
    cargo = datos.get('cargo', '').strip()
    activo = datos.get('estado_activo') == 'True'
    
    # Validaciones de formato
    if not validar_solo_letras(nombres) or not validar_solo_letras(apellidos):
        messages.error(request, "Error: Nombres y apellidos solo deben contener letras.")
        return
        
    if not cedula.isdigit():
        messages.error(request, "Error: La cédula debe contener únicamente números.")
        return
        
    if not telefono.isdigit():
        messages.error(request, "Error: El teléfono debe contener únicamente números.")
        return
        
    # Validación para evitar cédulas duplicadas en el sistema
    if Asesor.objects.filter(cedula=cedula).exists():
        messages.error(request, f"Error: La cédula {cedula} ya se encuentra registrada.")
        return
        
    # Creación en dos pasos por herencia multi-tabla
    nuevo_asesor_base = Asesor.objects.create(
        nombres=nombres, apellidos=apellidos, cedula=cedula, telefono=telefono, correo=correo
    )
    AsesorAcademico.objects.create(
        asesor=nuevo_asesor_base, profesion=profesion, dependencia=dependencia, cargo=cargo, activo=activo 
    )
    messages.success(request, f"Asesor {nombres} {apellidos} registrado exitosamente.")

def editar_asesor_academico(request, datos):
    """
    Actualiza los datos de un Asesor Académico existente.
    Valida los formatos y asegura que si se cambia la cédula, 
    esta no le pertenezca ya a otro asesor registrado.
    """
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

    # Validaciones de formato
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

        # Comprobamos que la nueva cédula no choque con la de otro asesor distinto
        if Asesor.objects.filter(cedula=cedula).exclude(id=asesor_base.id).exists():
            messages.error(request, f"Error: La cédula {cedula} ya pertenece a otro asesor.")
            return

        # 1. Actualizamos el modelo base (Asesor)
        asesor_base.nombres = nombres
        asesor_base.apellidos = apellidos
        asesor_base.cedula = cedula
        asesor_base.telefono = telefono
        asesor_base.correo = correo
        asesor_base.save()

        # 2. Actualizamos el modelo académico (AsesorAcademico)
        asesor_academico.profesion = profesion
        asesor_academico.dependencia = dependencia
        asesor_academico.cargo = cargo
        asesor_academico.activo = activo
        asesor_academico.save()

        messages.success(request, "Asesor académico actualizado correctamente.")

    except AsesorAcademico.DoesNotExist:
        messages.error(request, "Error: No se pudo encontrar el asesor a editar.")


def cambiar_estado_asesor(request, datos):
    """
    Alterna el estado lógico de un asesor (de Activo a Inactivo y viceversa).
    """
    asesor_id = datos.get('id')
    try:
        # CORRECCIÓN: Buscamos por asesor_id aquí también
        asesor = AsesorAcademico.objects.get(asesor_id=asesor_id)
        # Invertimos el valor booleano
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