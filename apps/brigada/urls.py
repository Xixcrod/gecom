from django.urls import path
from . import views

urlpatterns = [
    path('', views.brigada_periodo, name="brigada_periodo"), #Ruta principal de la aplicación que lleva a la vista de los periodos de brigada
    path('brigadas/<uuid:periodo_id>/', views.brigadas, name='brigadas'), #Ruta para mostrar las brigadas de un periodo específico
]