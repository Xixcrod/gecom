from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse

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
            return render(request, 'login.html', {  'error': "Por favor, completa todos los campos."})

        # Autenticación estándar de Django
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            # VERIFICACIÓN CRÍTICA: Solo el Superusuario entra
            if user.is_superuser:
                login(request, user)
                return redirect('index') # Redirección al panel administrativo
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

            # 1. Generar token y ID codificado
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))


            # 2. Construir la URL (asegúrate de tener esta ruta en urls.py)
            protocol = 'https' if request.is_secure() else 'http'
            domain = request.get_host()
            link = reverse('reset_password_confirm', kwargs={'uidb64': uid, 'token': token})
            url_completa = f"{protocol}://{domain}{link}"

            # 3. Enviar el correo
            asunto = 'Restablecer Contraseña Administrativa'
            mensaje = (
                f'Hola {user.username},\n\n'
                f'Haz clic en el siguiente enlace para cambiar tu contraseña:\n{url_completa}\n\n'
                f'Este enlace es de un solo uso y expirará pronto.'
            )
            
            send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [email_input])

            return render(request, 'login.html', {'success': 'Se ha enviado un enlace de recuperación a tu correo.'})

        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Datos incorrectos.'})
    
    return render(request, 'recuperar_contrasena.html')



# @login_excluded('dashboard')
def reset_password_confirm(request, uidb64, token):
    """
    función para manejar la confirmación del restablecimiento de contraseña. Verifica el token y permite al usuario ingresar una nueva contraseña. De acuerdo si es GET o POST, muestra el formulario o procesa la nueva contraseña respectivamente.
    """
    try:
        # Decodificar el ID del usuario
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Validar que el usuario existe y el token es válido
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            nueva_pass = request.POST.get('password')
            confirm_pass = request.POST.get('confirm_password')

            if nueva_pass == confirm_pass:
                user.set_password(nueva_pass)
                user.save()
                return render(request, 'login.html', {'success': 'Contraseña actualizada correctamente.'})
            else:
                return render(request, 'nueva_contrasena.html', {'error': 'Las contraseñas no coinciden.'})
        
        # Si es GET, mostramos el formulario para escribir la clave
        return render(request, 'nueva_contrasena.html')
    else:
        return render(request, 'login.html', {'error': 'El enlace ha expirado o es inválido.'})