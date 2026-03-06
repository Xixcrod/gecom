from django.urls import path
from . import views
from .utils import brigada_detalles, brigadas

urlpatterns = [
    path('', views.brigada_periodo, name="brigada_periodo"), #Ruta principal de la aplicación que lleva a la vista de los periodos de brigada
    path('brigadas/<uuid:periodo_id>/', views.brigadas, name='brigadas'), #Ruta para mostrar las brigadas de un periodo específico
    path('brigada/<uuid:brigada_id>/', views.brigada_detalles, name='brigada_detalles'), #Ruta para mostrar los detalles de una brigada específica
    path('brigada/<uuid:periodo_id>/brigadas/crear/', brigadas.crear_brigada, name='crear_brigada'), #Ruta para crear una nueva brigada en un periodo específico
    path('<uuid:brigada_id>/guardar-comunitario/', brigada_detalles.guardar_asesor_comunitario, name='guardar_comunitario'), #Ruta para guardar o actualizar un asesor comunitario para una brigada específica
    path('<uuid:brigada_id>/asignar-academico/', brigada_detalles.asignar_asesor_academico, name='asignar_academico'), #Ruta para asignar un asesor académico a una brigada específica
]