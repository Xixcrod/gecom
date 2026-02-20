from django.urls import path
from . import views

urlpatterns = [
    path('periodo', views.periodo, name="periodo"), #Ruta principal de la aplicación que lleva al login
]