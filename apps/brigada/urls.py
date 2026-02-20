from django.urls import path
from . import views

urlpatterns = [
    path('', views.brigada, name="brigada"), #Ruta principal de la aplicación que lleva al login
]