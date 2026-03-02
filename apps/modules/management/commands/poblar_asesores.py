# apps/modules/management/commands/poblar_asesores.py
import random
from django.core.management.base import BaseCommand
from apps.core.models import Asesor, AsesorAcademico

class Command(BaseCommand):
    help = 'Puebla la base de datos con 25 asesores académicos aleatorios y realistas'

    def handle(self, *args, **kwargs):
        # 1. LIMPIEZA EN CASCADA
        # Como AsesorAcademico depende de Asesor (OneToOneField), borramos primero 
        # a los hijos y luego a los padres para no dejar datos huérfanos.
        AsesorAcademico.objects.all().delete()
        Asesor.objects.all().delete()

        # 2. DICCIONARIOS DE DATOS SEMILLA
        # Separamos los nombres por género para evitar combinaciones ilógicas (Ej: María Carlos)
        nombres_masculinos = ["Carlos", "Juan", "Luis", "Pedro", "Miguel", "Jesús", "José", "Rafael", "Víctor", "Enmanuel", "Andrés", "Diego", "Alejandro", "Gabriel"]
        nombres_femeninos = ["María", "Ana", "Laura", "Sofía", "Elena", "Isabella", "Carmen", "Patricia", "Gabriela", "Valeria", "Daniela", "Camila", "Andrea", "Victoria"]
        apellidos_list = ["Pérez", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Gómez", "Díaz", "Hernández", "Márquez", "García", "Rojas", "Silva", "Mendoza", "Castillo"]
        prefijos_telefonicos = ["0414", "0424", "0412", "0416", "0426"] # Prefijos venezolanos
        
        profesiones = ["Ing. en Informática", "Ing. Civil", "Lic. en Educación", "Ing. Industrial", "Médico Cirujano", "Médico Veterinario", "Lic. en Administración", "Ing. Agrónomo"]
        dependencias = [
            "Dpto. de Informática y Tecnología", "Dpto. de Física y Matemáticas", 
            "Dpto. de Ciencias de la Salud", "Dpto. de Ciencias de la Educación", 
            "Dpto. de Ciencias Agronómicas", "Coordinación de Servicio Comunitario"
        ]
        cargos = ["Profesor Titular", "Profesor Agregado", "Profesor Asistente", "Instructor", "Coordinador de Pasantías"]

        asesores_creados = 0

        # 3. BUCLE DE GENERACIÓN
        for i in range(25):
            genero = random.choice(['M', 'F'])
            
            # random.sample toma 2 elementos únicos de la lista sin repetir el mismo nombre
            if genero == 'M':
                nombres = random.sample(nombres_masculinos, 2)
            else:
                nombres = random.sample(nombres_femeninos, 2)
            
            apellidos = random.sample(apellidos_list, 2)
            
            # Armamos los strings finales para la base de datos
            nombre_generado = f"{nombres[0]} {nombres[1]}"
            apellido_generado = f"{apellidos[0]} {apellidos[1]}"
            cedula_generada = str(random.randint(10000000, 30000000))
            telefono_generado = f"{random.choice(prefijos_telefonicos)}{random.randint(1000000, 9999999)}"
            
            # Creamos un correo institucional simulado (Ej: carlos.perez42@gmail.com)
            correo_generado = f"{nombres[0].lower()}.{apellidos[0].lower()}{random.randint(1,99)}@gmail.com"

            profesion_generada = random.choice(profesiones)
            dependencia_generada = random.choice(dependencias)
            cargo_generado = random.choice(cargos)
            
            # Generamos un booleano ponderado: 80% probabilidad de ser True (Activo)
            estado_activo = random.choices([True, False], weights=[80, 20])[0] 

            # Verificamos que la cédula aleatoria no choque con una ya creada
            if not Asesor.objects.filter(cedula=cedula_generada).exists():
                
                # 4. GUARDADO EN DOS PASOS (Por la herencia de modelos)
                # Paso A: Se crea el perfil base con los datos de contacto
                asesor_base = Asesor.objects.create(
                    nombres=nombre_generado,
                    apellidos=apellido_generado,
                    cedula=cedula_generada,
                    telefono=telefono_generado,
                    correo=correo_generado
                )
                
                # Paso B: Se crea el perfil académico y se vincula mediante ForeignKey/OneToOne al perfil base
                AsesorAcademico.objects.create(
                    asesor=asesor_base,
                    profesion=profesion_generada,
                    dependencia=dependencia_generada,
                    cargo=cargo_generado,
                    activo=estado_activo
                )
                asesores_creados += 1

        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se han creado {asesores_creados} asesores académicos.'))