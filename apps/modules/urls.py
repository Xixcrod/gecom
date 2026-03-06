# apps/modules/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name="index"),
    path('periodo', views.periodo, name="periodo"),
    path('carrera/', views.carrera, name='carrera'),
    path('asesores-academicos/', views.asesores_academicos, name='asesores_academicos'),
    path('asesores-academicos/<uuid:asesor_id>/', views.detalle_asesor, name='detalle_asesor'),
]