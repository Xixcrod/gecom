from django.urls import path
from . import views
from .utils import login, servicios_respaldo

urlpatterns = [
    path('', views.signin, name="login"), #Ruta principal de la aplicación que lleva al login
    path('login-process/', login.loginProcess, name="login-process"), #Ruta para procesar el inicio de sesión
    path('logout/', views.signout, name="logout"), #Ruta para cerrar sesión
    path('recuperar_contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),#Ruta para la página de recuperación de contraseña
    path('processing_password/', login.recovering_password, name="processing_password"), #Ruta para procesar la solicitud de recuperación de contraseña
    path('nueva_contrasena/', views.nueva_contrasena, name="nueva_contrasena"), #Ruta para la página de nueva contraseña
    path('restablecer/<uidb64>/<token>/', login.reset_password_confirm, name='reset_password_confirm'), #Ruta para confirmar el restablecimiento de contraseña con token
    path('respaldo/', views.respaldo, name='respaldo'), #Ruta para la página de respaldo y restauración, accesible solo para superusuarios
    path('backup/crear/', views.trigger_backup, name='hacer_respaldo'),#Ruta para crear un respaldo de la base de datos y archivos multimedia, solo accesible para superusuarios
    path('backup/restaurar/', views.trigger_restore, name='hacer_restauracion'),#Ruta para restaurar la base de datos y archivos multimedia desde el último respaldo, solo accesible para superusuarios
    path('backup/restore_status/', servicios_respaldo.check_restore_status, name='restore_status'),#Ruta para que el frontend consulte el estado del proceso de restauración
]