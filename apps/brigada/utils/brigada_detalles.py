from django.shortcuts import get_object_or_404
from apps.core.models import Brigada, AsesorAcademico, AsesorComunitario, BrigadaAsesor, Asesor, Proyecto, Estudiante, Carrera
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.contrib import messages
from django.shortcuts import redirect

def obtener_contexto_brigada_detalles(brigada_id):
    '''Obtiene el contexto necesario para la vista de detalles de una brigada, incluyendo información sobre la brigada, su proyecto asociado, estudiantes y asesores.'''
    brigada = get_object_or_404(
        Brigada.objects.select_related('periodo').prefetch_related('estudiantes__carrera'),
        id=brigada_id
    )
    proyecto = brigada.proyectos.first()

    # Buscamos los enlaces en BrigadaAsesor
    academico_link = brigada.brigadaasesor_set.filter(rol='ACADEMICO').first()
    comunitario_link = brigada.brigadaasesor_set.filter(rol='COMUNITARIO').first()

    # Extraemos la instancia hija correspondiente si existe
    asesor_academico = None
    if academico_link and hasattr(academico_link.asesor, 'asesoracademico'):
        asesor_academico = academico_link.asesor.asesoracademico

    asesor_comunitario = None
    if comunitario_link and hasattr(comunitario_link.asesor, 'asesorcomunitario'):
        asesor_comunitario = comunitario_link.asesor.asesorcomunitario

    # Lista de académicos activos para el selector
    academicos_activos = AsesorAcademico.objects.filter(activo=True).select_related('asesor')

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


def modificar_nombre_brigada(request, brigada_id):
    '''Modifica el nombre de una brigada específica, asegurando que el nuevo nombre sea un número entero único.'''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nuevo_nombre = data.get('nombre')

            # 1. Validación de valor entero
            if not str(nuevo_nombre).isdigit():
                return JsonResponse({
                    'success': False, 
                    'message': 'El nombre de la brigada debe ser un número entero sin letras.'
                }, status=400)

            # 2. Validación de existencia (Excluyendo la brigada actual)
            # Nota: filter().exclude() asegura que si no cambias el nombre, no dé error de "ya existe"
            if Brigada.objects.filter(nombre=nuevo_nombre).exclude(id=brigada_id).exists():
                return JsonResponse({
                    'success': False, 
                    'message': f'La brigada número {nuevo_nombre} ya existe en el sistema.'
                }, status=400)

            # 3. Actualización
            brigada = Brigada.objects.get(id=brigada_id)
            brigada.nombre = nuevo_nombre
            brigada.save()

            return JsonResponse({
                'success': True, 
                'message': 'Nombre de brigada actualizado correctamente.'
            })

        except Brigada.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Brigada no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
            
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


def guardar_asesor_comunitario(request, brigada_id):
    '''Guarda o actualiza un asesor comunitario, prohibiendo la reutilización de asesores académicos.'''
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Formato de datos inválido.'}, status=400)

    try:
        brigada = Brigada.objects.get(id=brigada_id)
        asesor_id = data.get('asesor_id')
        nueva_cedula = data.get('cedula')

        # Validación de campos obligatorios
        campos_requeridos = ['nombres', 'apellidos', 'cedula', 'telefono', 'correo']
        for campo in campos_requeridos:
            if not data.get(campo) or str(data.get(campo)).strip() == '':
                return JsonResponse({'success': False, 'message': f'El campo "{campo}" es obligatorio.'}, status=400)

        if asesor_id:
            # --- 1. MODIFICAR EXISTENTE ---
            try:
                asesor = Asesor.objects.get(id=asesor_id)
            except Asesor.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Asesor no encontrado.'}, status=404)
            
            # Validar que la nueva cédula no la tenga OTRO asesor
            if Asesor.objects.filter(cedula=nueva_cedula).exclude(id=asesor_id).exists():
                return JsonResponse({
                    'success': False, 
                    'message': f'La cédula {nueva_cedula} ya está registrada en el sistema.'
                }, status=400)

            asesor.nombres = data['nombres']
            asesor.apellidos = data['apellidos']
            asesor.cedula = nueva_cedula
            asesor.telefono = data['telefono']
            asesor.correo = data['correo']
            asesor.save()
            mensaje = "Datos actualizados con éxito."

        else:
            # --- 2. CREAR O REUTILIZAR ---
            asesor_existente = Asesor.objects.filter(cedula=nueva_cedula).first()

            if asesor_existente:
                # VALIDACIÓN CLAVE: Verificar si es Asesor Académico
                # Usamos hasattr para comprobar la relación OneToOne inversa
                if hasattr(asesor_existente, 'asesoracademico'):
                    return JsonResponse({
                        'success': False, 
                        'message': f'La cédula {nueva_cedula} pertenece a un Asesor Académico. No puede ser reutilizado como Comunitario.'
                    }, status=400)

                asesor_objetivo = asesor_existente
                mensaje = "Asesor comunitario existente asignado a la brigada."
                AsesorComunitario.objects.get_or_create(asesor=asesor_objetivo)
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
                mensaje = "Asesor comunitario creado con éxito."

            # 3. Enlazar con la brigada
            BrigadaAsesor.objects.get_or_create(
                brigada=brigada, 
                asesor=asesor_objetivo, 
                rol='COMUNITARIO'
            )

        return JsonResponse({'success': True, 'message': mensaje})

    except Brigada.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Brigada no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

        return JsonResponse({'success': True, 'message': mensaje})

    except Brigada.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'La brigada especificada no se encuentra en el sistema.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'}, status=500)

def asignar_asesor_academico(request, brigada_id):
    '''Asigna un asesor académico a una brigada específica o modificarlo.'''
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Formato de datos (JSON) inválido.'}, status=400)

    asesor_base_id = data.get('asesor_base_id')
    
    # Validar que enviaron el ID
    if not asesor_base_id:
        return JsonResponse({'success': False, 'message': 'No se proporcionó el ID del asesor base.'}, status=400)

    try:
        # Manejo explícito de las consultas
        brigada = Brigada.objects.get(id=brigada_id)
        asesor_base = Asesor.objects.get(id=asesor_base_id)
        
        # update_or_create es excelente aquí
        link, created = BrigadaAsesor.objects.update_or_create(
            brigada=brigada,
            rol='ACADEMICO',
            defaults={'asesor': asesor_base}
        )
        return JsonResponse({'success': True, 'message': 'Asesor académico asignado con éxito.'})

    except Brigada.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'La brigada especificada no existe.'}, status=404)
    except Asesor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El asesor base seleccionado no existe en el sistema.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al asignar el asesor: {str(e)}'}, status=500)
    

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
            return JsonResponse({
                'success': False,
                'message': 'No se puede crear el proyecto: La brigada no tiene un Asesor Académico asignado.'
            }, status=400)

        # 2. Captura manual de datos desde el formulario HTML
        nombre = request.POST.get('nombre_proyecto')
        comunidad = request.POST.get('comunidad')
        f_inicio = request.POST.get('fecha_inicio')
        f_fin = request.POST.get('fecha_culminacion') # Puede venir vacío ''

        # Validación básica de campos requeridos para el JSON
        if not all([nombre, comunidad, f_inicio]):
            return JsonResponse({
                'success': False,
                'message': 'Faltan campos obligatorios (Nombre, Comunidad o Fecha de Inicio).'
            }, status=400)

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
            return JsonResponse({
            'success': True,
            'message': 'Proyecto registrado exitosamente.',
            })
            
        except AsesorAcademico.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'El asesor asignado no tiene un perfil académico completo.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar en la base de datos: {str(e)}'
            }, status=500)

    return redirect('brigada_detalles', brigada_id=brigada_id)


@require_POST
def guardar_estudiante_ajax(request, brigada_id, carrera_id):
    # 1. Obtener los datos del cuerpo del POST (enviados por el FormData de JS)
    nombres = request.POST.get('nombres')
    apellidos = request.POST.get('apellidos')
    cedula = request.POST.get('cedula')
    correo = request.POST.get('correo')
    telefono = request.POST.get('telefono')

    # 2. Validación de Cédula Duplicada (Requerimiento principal)
    if Estudiante.objects.filter(cedula=cedula).exists():
        return JsonResponse({
            'exito': False, 
            'mensaje': f'La cédula {cedula} ya está registrada en el sistema.'
        }, status=400)

    try:
        # 3. Obtener las instancias de los objetos por ID (vienen de la URL)
        brigada = get_object_or_404(Brigada, id=brigada_id)
        carrera = get_object_or_404(Carrera, id=carrera_id)

        # 4. Crear el registro del estudiante
        nuevo_estudiante = Estudiante.objects.create(
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            correo=correo,
            telefono=telefono,
            brigada=brigada,
            carrera=carrera
        )

        # 5. Respuesta exitosa con los datos necesarios para actualizar el HTML
        return JsonResponse({
            'exito': True,
            'mensaje': 'Estudiante agregado correctamente.',
            'estudiante': {
                'nombres': nuevo_estudiante.nombres,
                'apellidos': nuevo_estudiante.apellidos,
                'cedula': nuevo_estudiante.cedula,
                'carrera_nombre': carrera.nombre_carrera
            }
        })

    except Exception as e:
        return JsonResponse({
            'exito': False, 
            'mensaje': f'Ocurrió un error inesperado: {str(e)}'
        }, status=500)