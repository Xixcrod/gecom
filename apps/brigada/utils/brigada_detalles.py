from django.shortcuts import get_object_or_404, redirect
from apps.core.models import Brigada, AsesorAcademico, AsesorComunitario, BrigadaAsesor, Asesor, Proyecto, Estudiante, Carrera
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.contrib import messages
from datetime import datetime


def obtener_contexto_brigada_detalles(brigada_id):
    '''Obtiene el contexto necesario para la vista de detalles de una brigada, incluyendo información sobre la brigada, su proyecto asociado, estudiantes y asesores.'''
    brigada = get_object_or_404(
        Brigada.objects.select_related(
            'periodo').prefetch_related('estudiantes__carrera'),
        id=brigada_id
    )
    proyecto = brigada.proyectos.first()

    # Buscamos los enlaces en BrigadaAsesor
    academico_link = brigada.brigadaasesor_set.filter(rol='ACADEMICO').first()
    comunitario_link = brigada.brigadaasesor_set.filter(
        rol='COMUNITARIO').first()

    # Extraemos la instancia hija correspondiente si existe
    asesor_academico = None
    if academico_link and hasattr(academico_link.asesor, 'asesoracademico'):
        asesor_academico = academico_link.asesor.asesoracademico

    asesor_comunitario = None
    if comunitario_link and hasattr(comunitario_link.asesor, 'asesorcomunitario'):
        asesor_comunitario = comunitario_link.asesor.asesorcomunitario

    # Lista de académicos activos para el selector
    academicos_activos = AsesorAcademico.objects.filter(
        activo=True).select_related('asesor')

    carreras_disponibles = Carrera.objects.all().order_by('nombre_carrera')

    return {
        'brigada': brigada,
        'proyecto': proyecto,
        'estudiantes': brigada.estudiantes.all(),
        'asesor_academico': asesor_academico,
        'asesor_comunitario': asesor_comunitario,
        'academicos_activos': academicos_activos,
        'carreras': carreras_disponibles
    }

@login_required
def modificar_nombre_brigada(request, brigada_id):
    '''Modifica el nombre de una brigada específica, asegurando que el nuevo nombre sea un número entero único.'''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nuevo_nombre = data.get('nombre')

            # 1. Validación de valor entero
            if not str(nuevo_nombre).isdigit():
                return JsonResponse({'success': False, 'message': 'El nombre de la brigada debe ser un número entero sin letras.'}, status=400)

            # 2. Validación de existencia (Excluyendo la brigada actual)
            # Nota: filter().exclude() asegura que si no cambias el nombre, no dé error de "ya existe"
            if Brigada.objects.filter(nombre=nuevo_nombre).exclude(id=brigada_id).exists():
                return JsonResponse({'success': False, 'message': f'La brigada número {nuevo_nombre} ya existe en el sistema.'}, status=400)

            # 3. Actualización
            brigada = Brigada.objects.get(id=brigada_id)
            brigada.nombre = nuevo_nombre
            brigada.save()

            messages.success(
                request, 'Nombre de brigada actualizado correctamente.')
            return JsonResponse({'success': True})

        except Brigada.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Brigada no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
def guardar_asesor_comunitario(request, brigada_id):
    '''Guarda o actualiza un asesor comunitario, prohibiendo la reutilización de asesores académicos.'''
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        brigada = Brigada.objects.get(id=brigada_id)
        asesor_id = data.get('asesor_id')
        nueva_cedula = data.get('cedula')

        # Validación de campos obligatorios
        campos_requeridos = ['nombres', 'apellidos',
                             'cedula', 'telefono', 'correo']
        for campo in campos_requeridos:
            if not data.get(campo) or str(data.get(campo)).strip() == '':
                messages.error(request, f'El campo "{campo}" es obligatorio.')
                return JsonResponse({'success': False}, status=400)

        if asesor_id:
            # --- 1. MODIFICAR EXISTENTE ---
            try:
                asesor = Asesor.objects.get(id=asesor_id)
            except Asesor.DoesNotExist:
                messages.error(request, 'Asesor no encontrado.')
                return JsonResponse({'success': False}, status=404)

            # Validar que la nueva cédula no la tenga OTRO asesor
            if Asesor.objects.filter(cedula=nueva_cedula).exclude(id=asesor_id).exists():
                messages.error(
                    request, f'La cédula {nueva_cedula} ya está registrada.')
                return JsonResponse({'success': False}, status=400)

            asesor.nombres = data['nombres']
            asesor.apellidos = data['apellidos']
            asesor.cedula = nueva_cedula
            asesor.telefono = data['telefono']
            asesor.correo = data['correo']
            asesor.save()
            mensaje_exito = "Datos actualizados con éxito."

        else:
            # --- 2. CREAR O REUTILIZAR ---
            asesor_existente = Asesor.objects.filter(
                cedula=nueva_cedula).first()

            if asesor_existente:
                # VALIDACIÓN CLAVE: Verificar si es Asesor Académico
                # Usamos hasattr para comprobar la relación OneToOne inversa
                if hasattr(asesor_existente, 'asesoracademico'):
                    messages.error(
                        request, f'La cédula {nueva_cedula} pertenece a un Asesor Académico.')
                    return JsonResponse({'success': False}, status=400)

                asesor_objetivo = asesor_existente
                AsesorComunitario.objects.get_or_create(asesor=asesor_objetivo)
                mensaje_exito = "Asesor comunitario asignado a la brigada."

            else:
                # Si no existe en absoluto, se crea
                asesor_objetivo = Asesor.objects.create(
                    nombres=data['nombres'],
                    apellidos=data['apellidos'],
                    cedula=nueva_cedula,
                    telefono=data['telefono'],
                    correo=data['correo']
                )
                AsesorComunitario.objects.create(asesor=asesor_objetivo)
                mensaje_exito = "Asesor comunitario creado y asignado con éxito."

            # 3. Enlazar con la brigada
            BrigadaAsesor.objects.get_or_create(
                brigada=brigada,
                asesor=asesor_objetivo,
                rol='COMUNITARIO'
            )

        messages.success(request, mensaje_exito)
        return JsonResponse({'success': True})

    except Brigada.DoesNotExist:
        messages.error(request, 'Brigada no encontrada.')
        return JsonResponse({'success': False}, status=404)
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        return JsonResponse({'success': False}, status=500)

@login_required
def asignar_asesor_academico(request, brigada_id):
    '''Asigna un asesor académico a una brigada específica o modificarlo.'''
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        asesor_base_id = data.get('asesor_base_id')

        # Validar que enviaron el ID
        if not asesor_base_id:
            messages.error(request, 'No se proporcionó el ID del asesor base.')
            return JsonResponse({'success': False}, status=400)

        # Manejo explícito de las consultas
        brigada = Brigada.objects.get(id=brigada_id)
        asesor_base = Asesor.objects.get(id=asesor_base_id)

        link, created = BrigadaAsesor.objects.update_or_create(
            brigada=brigada,
            rol='ACADEMICO',
            defaults={'asesor': asesor_base}
        )

        # Mensaje de éxito dinámico
        msg = 'Asesor académico asignado con éxito.' if created else 'Asesor académico actualizado correctamente.'
        messages.success(request, msg)
        return JsonResponse({'success': True})

    except Brigada.DoesNotExist:
        messages.error(request, 'La brigada especificada no existe.')
        return JsonResponse({'success': False}, status=404)
    except Asesor.DoesNotExist:
        messages.error(
            request, 'El asesor seleccionado no existe en el sistema.')
        return JsonResponse({'success': False}, status=404)
    except Exception as e:
        messages.error(request, f'Error al asignar el asesor: {str(e)}')
        return JsonResponse({'success': False}, status=500)


@login_required
def procesar_proyecto(request, brigada_id):
    '''Procesa la creación de un nuevo proyecto dentro de una brigada específica, asegurando que la brigada tenga un asesor académico asignado.'''
    if request.method == 'POST':
        brigada = get_object_or_404(Brigada, id=brigada_id)

        # 1. Validación de Existencia del Asesor Académico
        enlace_academico = BrigadaAsesor.objects.filter(
            brigada=brigada,
            rol=BrigadaAsesor.Rol.ACADEMICO
        ).first()

        if not enlace_academico:
            messages.error(
                request, 'No se puede crear el proyecto: La brigada no tiene un Asesor Académico asignado.')
            return JsonResponse({'success': False}, status=400)

        # 2. Captura manual de datos desde el formulario HTML
        nombre = request.POST.get('nombre_proyecto')
        comunidad = request.POST.get('comunidad')
        f_inicio = request.POST.get('fecha_inicio')
        f_fin = request.POST.get('fecha_culminacion')  # Puede venir vacío ''

        # Validación básica de campos requeridos para el JSON
        if not all([nombre, comunidad, f_inicio]):
            messages.error(
                request, 'Faltan campos obligatorios (Nombre, Comunidad o Fecha de Inicio).')
            return JsonResponse({'success': False}, status=400)

        if f_fin:
            try:
                # Los input type="date" de HTML5 envían los datos en formato YYYY-MM-DD
                formato = "%Y-%m-%d"
                fecha_inicio_obj = datetime.strptime(f_inicio, formato).date()
                fecha_fin_obj = datetime.strptime(f_fin, formato).date()

                if fecha_fin_obj < fecha_inicio_obj:
                    messages.error(
                        request, 'Error: La fecha de culminación no puede ser anterior a la fecha de inicio.')
                    return JsonResponse({'success': False}, status=400)
            except ValueError:
                # Se dispara si alguien manipula el HTML y envía algo que no es una fecha válida
                messages.error(
                    request, 'El formato de las fechas proporcionadas es inválido.')
                return JsonResponse({'success': False}, status=400)

        # 3. Creación del objeto Proyecto
        try:
            # Obtenemos la instancia de AsesorAcademico vinculada
            instancia_academico = enlace_academico.asesor.asesoracademico

            proyecto = Proyecto(
                nombre_proyecto=nombre,
                comunidad=comunidad,
                fecha_inicio=f_inicio,
                brigada=brigada,
                asesor_academico=instancia_academico
            )

            # Validamos si la fecha de fin trae datos (si es '', se guarda como None/Null)
            if f_fin:
                proyecto.fecha_culminacion = f_fin

            proyecto.save()
            messages.success(request, 'Proyecto registrado exitosamente.')
            return JsonResponse({'success': True})

        except AsesorAcademico.DoesNotExist:
            messages.error(
                request, 'El asesor asignado no tiene un perfil académico completo.')
            return JsonResponse({'success': False}, status=400)
        except Exception as e:
            messages.error(
                request, f'Error al guardar en la base de datos: {str(e)}')
            return JsonResponse({'success': False}, status=500)

    return redirect('brigada_detalles', brigada_id=brigada_id)


@login_required
def guardar_estudiante_ajax(request, brigada_id, carrera_id):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)

    # 1. Obtener los datos del cuerpo del POST (enviados por el FormData de JS)
    nombres = request.POST.get('nombres')
    apellidos = request.POST.get('apellidos')
    cedula = request.POST.get('cedula')
    correo = request.POST.get('correo')
    telefono = request.POST.get('telefono')

    # Validación de campos vacíos en backend
    if not all([nombres, apellidos, cedula]):
        messages.error(
            request, 'Faltan campos obligatorios (Nombres, Apellidos y Cédula).')
        return JsonResponse({'success': False}, status=400)

    # 2. Validación de Cédula Duplicada (Requerimiento principal)
    if Estudiante.objects.filter(cedula=cedula).exists():
        messages.error(
            request, f'La cédula {cedula} ya está registrada en el sistema.')
        return JsonResponse({'success': False}, status=400)

    try:
        # 3. Obtener las instancias de los objetos por ID (vienen de la URL)
        brigada = get_object_or_404(Brigada, id=brigada_id)
        carrera = get_object_or_404(Carrera, id=carrera_id)

        # 4. Crear el registro del estudiante
        Estudiante.objects.create(
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            correo=correo,
            telefono=telefono,
            brigada=brigada,
            carrera=carrera
        )

        # 5. Respuesta exitosa con los datos necesarios para actualizar el HTML
        messages.success(request, 'Estudiante agregado correctamente.')
        return JsonResponse({'success': True})

    except Exception as e:
        messages.error(request, f'Ocurrió un error inesperado: {str(e)}')
        return JsonResponse({'success': False}, status=500)
