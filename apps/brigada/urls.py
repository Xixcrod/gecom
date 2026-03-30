from django.urls import path
from . import views
from .utils import brigada_detalles, brigadas, proyecto_documentos, estudiante_detalles

urlpatterns = [
    path('', views.brigada_periodo, name="brigada_periodo"), #Ruta principal de la aplicación que lleva a la vista de los periodos de brigada
    path('brigadas/<uuid:periodo_id>/', views.brigadas, name='brigadas'), #Ruta para mostrar las brigadas de un periodo específico
    path('brigada/<uuid:brigada_id>/', views.brigada_detalles, name='brigada_detalles'), #Ruta para mostrar los detalles de una brigada específica
    path('brigada/<uuid:periodo_id>/brigadas/crear/', brigadas.crear_brigada, name='crear_brigada'), #Ruta para crear una nueva brigada en un periodo específico
    path('brigada/<uuid:brigada_id>/brigada/modificar/', brigada_detalles.modificar_nombre_brigada, name='modificar_nombre_brigada'), #Ruta para modificar el nombre de una brigada específica
    path('<uuid:brigada_id>/guardar-comunitario/', brigada_detalles.guardar_asesor_comunitario, name='guardar_comunitario'), #Ruta para guardar o actualizar un asesor comunitario para una brigada específica
    path('<uuid:brigada_id>/asignar-academico/', brigada_detalles.asignar_asesor_academico, name='asignar_academico'), #Ruta para asignar un asesor académico a una brigada específica
    path('<uuid:brigada_id>/proyecto/nuevo/', brigada_detalles.procesar_proyecto, name='guardar_proyecto'), #Ruta para procesar la creación de un nuevo proyecto dentro de una brigada específica
    path('<uuid:brigada_id>/<uuid:carrera_id>/estudiante/agregar/', brigada_detalles.guardar_estudiante_ajax, name='guardar_estudiante'), #Ruta para procesar la creación de un nuevo estudiante dentro de una brigada y carrera específica
    path('<uuid:brigada_id>/proyecto/<uuid:proyecto_id>/', views.proyecto_documentos, name='proyecto_documentos'),
    path('proyecto/<uuid:proyecto_id>/subir-documento/<str:tipo_documento>/', proyecto_documentos.subir_documento_proyecto, name='subir_documento_proyecto'), #Ruta para subir un documento a un proyecto específico dentro de una brigada
    path('estudiante/<uuid:estudiante_id>/detalles/', views.estudiante_detalles, name='estudiante_detalles'), #Ruta para mostrar los detalles de un estudiante específico
    path('estudiante/<uuid:estudiante_id>/subir-certificado/', estudiante_detalles.subir_certificado_estudiante, name='subir_certificado_estudiante'), #Ruta para subir el certificado de un estudiante específico
]