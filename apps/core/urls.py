from django.urls import path
from . import views

urlpatterns = [
    path('', views.signin, name="login"), #Ruta principal de la aplicación que lleva al login
]