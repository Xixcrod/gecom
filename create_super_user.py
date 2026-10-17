import os
import django

# 1. Configurar el entorno de Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gecom.settings')
django.setup()

from django.contrib.auth import get_user_model

Usuario = get_user_model()

def ejecutar_inicializacion():
    """
    Función para automatizar la creación del superusuario en el arranque o despliegue.
    """
    # ----------------------------------------------------
    # CREACIÓN DEL SUPERUSUARIO
    # ----------------------------------------------------
    username_admin = os.getenv('SUPERUSER_USERNAME', '12345678')
    email_admin = os.getenv('SUPERUSER_EMAIL', 'admin@example.com')
    password_admin = os.getenv('SUPERUSER_PASSWORD', 'user12345')
    first_name_admin = os.getenv('SUPERUSER_FIRST_NAME', 'Admin')
    last_name_admin = os.getenv('SUPERUSER_LAST_NAME', 'Sistema')

    # Verificamos si el superusuario ya existe basándonos en el username
    if not Usuario.objects.filter(username=username_admin).exists():
        print(f"Creando superusuario con username: {username_admin}...")
        
        try:
            cedula_admin = os.getenv('SUPERUSER_CEDULA', '12345678')
            telefono_admin = os.getenv('SUPERUSER_TELEFONO', '04111234567')
            
            Usuario.objects.create_superuser(
                cedula=cedula_admin,
                username=username_admin,
                first_name=first_name_admin,
                last_name=last_name_admin,
                email=email_admin,
                password=password_admin,
                telefono=telefono_admin
            )
            print("Superusuario creado exitosamente (con campos personalizados).")
            
        except TypeError:
            Usuario.objects.create_superuser(
                username=username_admin,
                email=email_admin,
                password=password_admin,
                first_name=first_name_admin,
                last_name=last_name_admin
            )
            print("Superusuario creado exitosamente (con campos estándar de Django).")
    else:
        print(f"El superusuario con username '{username_admin}' ya existe.")

if __name__ == '__main__':
    ejecutar_inicializacion()