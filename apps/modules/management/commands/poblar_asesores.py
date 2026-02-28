# apps/modules/management/commands/poblar_asesores.py
import random
from django.core.management.base import BaseCommand
from apps.core.models import Asesor, AsesorAcademico

class Command(BaseCommand):
    help = 'Puebla la base de datos con 25 asesores académicos aleatorios y realistas'

    def handle(self, *args, **kwargs):
        AsesorAcademico.objects.all().delete()
        Asesor.objects.all().delete()

        # Separamos por género para evitar combinaciones ilógicas
        nombres_masculinos = ["Carlos", "Juan", "Luis", "Pedro", "Miguel", "Jesús", "José", "Rafael", "Víctor", "Enmanuel", "Andrés", "Diego", "Alejandro", "Gabriel"]
        nombres_femeninos = ["María", "Ana", "Laura", "Sofía", "Elena", "Isabella", "Carmen", "Patricia", "Gabriela", "Valeria", "Daniela", "Camila", "Andrea", "Victoria"]
        
        apellidos_list = ["Pérez", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Gómez", "Díaz", "Hernández", "Márquez", "García", "Rojas", "Silva", "Mendoza", "Castillo"]
        
        prefijos_telefonicos = ["0414", "0424", "0412", "0416", "0426"]
        
        profesiones = ["Ing. en Informática", "Ing. Civil", "Lic. en Educación", "Ing. Industrial", "Médico Cirujano", "Médico Veterinario", "Lic. en Administración", "Ing. Agrónomo"]
        
        dependencias = [
            "Dpto. de Informática y Tecnología", 
            "Dpto. de Física y Matemáticas", 
            "Dpto. de Ciencias de la Salud", 
            "Dpto. de Ciencias de la Educación", 
            "Dpto. de Ciencias Agronómicas",
            "Coordinación de Servicio Comunitario"
        ]
        
        cargos = ["Profesor Titular", "Profesor Agregado", "Profesor Asistente", "Instructor", "Coordinador de Pasantías"]

        asesores_creados = 0

        for i in range(25):
            # 1. Decidir el género al azar
            genero = random.choice(['M', 'F'])
            
            # 2. Tomar 2 nombres distintos de la lista correspondiente
            if genero == 'M':
                nombres = random.sample(nombres_masculinos, 2)
            else:
                nombres = random.sample(nombres_femeninos, 2)
            
            # 3. Tomar 2 apellidos distintos
            apellidos = random.sample(apellidos_list, 2)
            
            nombre_generado = f"{nombres[0]} {nombres[1]}"
            apellido_generado = f"{apellidos[0]} {apellidos[1]}"
            
            # 4. Generar Cédula solo con números
            cedula_generada = str(random.randint(10000000, 30000000))
            
            # 5. Generar Teléfono con prefijos venezolanos
            telefono_generado = f"{random.choice(prefijos_telefonicos)}{random.randint(1000000, 9999999)}"
            
            # 6. Generar Correo de Gmail (le añadimos un número para asegurar que sean únicos)
            correo_generado = f"{nombres[0].lower()}.{apellidos[0].lower()}{random.randint(1,99)}@gmail.com"

            profesion_generada = random.choice(profesiones)
            dependencia_generada = random.choice(dependencias)
            cargo_generado = random.choice(cargos)
            
            estado_activo = random.choices([True, False], weights=[80, 20])[0] 

            if not Asesor.objects.filter(cedula=cedula_generada).exists():
                asesor_base = Asesor.objects.create(
                    nombres=nombre_generado,
                    apellidos=apellido_generado,
                    cedula=cedula_generada,
                    telefono=telefono_generado,
                    correo=correo_generado
                )
                
                AsesorAcademico.objects.create(
                    asesor=asesor_base,
                    profesion=profesion_generada,
                    dependencia=dependencia_generada,
                    cargo=cargo_generado,
                    activo=estado_activo
                )
                asesores_creados += 1

        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se han creado {asesores_creados} asesores académicos de prueba.'))