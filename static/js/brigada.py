import os
import django
import random
from faker import Faker

# 1. Configuración del entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gecom.settings') # <--- CAMBIA 'tu_proyecto' por el nombre de tu carpeta de settings
django.setup()

from apps.core.models import Periodo, Brigada, Estudiante, Carrera # <--- AJUSTA TUS IMPORTS

fake = Faker(['es_ES']) # Datos en español

def poblar_datos(nombre_periodo, cantidad_brigadas=20):
    print(f"--- Iniciando población para el periodo: {nombre_periodo} ---")

    # 1. Obtener o crear el periodo
    periodo, created = Periodo.objects.get_or_create(nombre=nombre_periodo)
    
    # 2. Crear un par de carreras si no existen
    carreras = ["Ingeniería Informática", "Licenciatura en Administración", "Ingeniería Industrial"]
    carreras_objs = []
    for c in carreras:
        obj, _ = Carrera.objects.get_or_create(nombre_carrera=c)
        carreras_objs.append(obj)

    # 3. Crear Brigadas y Estudiantes
    for i in range(1, cantidad_brigadas + 1):
        # El nombre de la brigada es un número entero según tu requerimiento
        nombre_b = str(i) 
        
        brigada = Brigada.objects.create(
            nombre=nombre_b,
            periodo=periodo
        )
        
        # Crear entre 5 y 10 estudiantes por brigada
        num_estudiantes = random.randint(5, 10)
        for _ in range(num_estudiantes):
            Estudiante.objects.create(
                nombres=fake.first_name(),
                apellidos=fake.last_name(),
                cedula=str(fake.unique.random_int(min=10000000, max=30000000)),
                correo=fake.email(),
                telefono=fake.phone_number()[:20],
                brigada=brigada,
                carrera=random.choice(carreras_objs)
            )
        
        print(f"Creada Brigada #{nombre_b} con {num_estudiantes} estudiantes.")

    print(f"\n¡Éxito! Se han creado {cantidad_brigadas} brigadas en el periodo {nombre_periodo}.")

if __name__ == '__main__':
    # Puedes cambiar el nombre del periodo aquí para que coincida con tus pruebas
    poblar_datos("I-2026-II-2027", cantidad_brigadas=25)