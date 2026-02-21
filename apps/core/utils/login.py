from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings

# @login_excluded('dashboard')
def loginProcess(request):

    """
    Esta funcion verifica la existencia del usuario cuyas credenciales recibe desde el método POST
    y de existir, loguea al usuario y lo redirecciona al inicio.
    """

    if request.method == 'POST':
        # En tu caso, el 'username' del superusuario suele ser su nombre o cédula
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')

        if not username_input or not password_input:
            return render(request, 'login.html', {'error': "Por favor, completa todos los campos."})

        # Autenticación estándar de Django
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            # VERIFICACIÓN CRÍTICA: Solo el Superusuario entra
            if user.is_superuser:
                login(request, user)
                return redirect('dashboard') # Redirección al panel administrativo
            else:
                # Si por error existe un usuario normal, le denegamos el acceso
                return render(request, 'login.html', {'error': "Acceso restringido solo para administradores."})
        else:
            return render(request, 'login.html', {'error': "Credenciales incorrectas."})
    
    # Si es GET, simplemente mostramos el login
    return render(request, 'login.html')


# @login_excluded('dashboard')
def recovering_password(request):
    """
    Recupera la contraseña del administrador verificando cédula (username) y email.
    """
    if request.method == 'POST':
        cedula_input = request.POST.get('username')
        email_input = request.POST.get('email')

        try:
            # 1. Buscamos al SUPERUSUARIO que coincida con la cédula (username) Y el email
            # Filtramos por is_superuser=True para mayor seguridad
            user = User.objects.get(
                username=cedula_input, 
                email=email_input, 
                is_superuser=True
            )

            # 2. Generar una contraseña aleatoria
            new_password = get_random_string(length=10)

            # 3. Guardar la nueva contraseña encriptada
            # set_password se encarga del hashing automáticamente
            user.set_password(new_password)
            user.save()

            # 4. Enviar el correo electrónico
            asunto = 'Recuperación de Acceso Administrativo'
            mensaje = (
                f'Hola {user.first_name or user.username},\n\n'
                f'Se ha restablecido tu acceso al sistema.\n'
                f'Tu nueva contraseña es: {new_password}\n\n'
                f'Por seguridad, copia la contraseña y borra el correo después de usarla. Si no solicitaste este cambio, por favor contacta al soporte inmediatamente.'
            )
            
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [email_input],
                fail_silently=False,
            )

            # 5. Éxito
            return render(request, 'login.html', {
                'success': True
            })

        except User.DoesNotExist:
            # 6. Error si no existe o no es superusuario
            return render(request, 'login.html', {
                'error': 'Los datos no coinciden con una cuenta de administrador activa.'
            })

        except Exception as e:
            return render(request, 'login.html', {
                'error': f'Error en el servidor de correo: {str(e)}'
            })

    # Si es GET, mostramos el formulario
    return render(request, 'recuperar_contrasena.html')