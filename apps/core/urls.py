from django.urls import path
from . import views
from .utils import login

urlpatterns = [
    path('', views.signin, name="login"), #Ruta principal de la aplicación que lleva al login
    path('login-process/', login.loginProcess, name="login-process"), #Ruta para procesar el inicio de sesión
    path('logout/', views.signout, name="logout"), #Ruta para cerrar sesión
    path('recuperar_contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),#Ruta para la página de recuperación de contraseña
    path('processing_password/', login.recovering_password, name="processing_password"), #Ruta para procesar la solicitud de recuperación de contraseña
    path('nueva_contrasena/', views.nueva_contrasena, name="nueva_contrasena"), #Ruta para la página de nueva contraseña
    path('restablecer/<uidb64>/<token>/', login.reset_password_confirm, name='reset_password_confirm'), #Ruta para confirmar el restablecimiento de contraseña con token
]