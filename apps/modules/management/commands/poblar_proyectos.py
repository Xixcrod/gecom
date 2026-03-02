# apps/modules/management/commands/poblar_proyectos.py
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.core.models import Periodo, AsesorAcademico, Brigada, BrigadaAsesor, Proyecto

class Command(BaseCommand):
    help = 'Puebla la BD con brigadas y proyectos de prueba vinculados a los asesores'

    def handle(self, *args, **kwargs):
        # 1. LIMPIEZA DE TABLAS DEPENDIENTES
        # Borramos en orden inverso a la creación para no violar restricciones de llaves foráneas
        Proyecto.objects.all().delete()
        BrigadaAsesor.objects.all().delete()
        Brigada.objects.all().delete()

        # 2. OBTENER LLAVES FORÁNEAS DISPONIBLES
        periodos = list(Periodo.objects.all())
        asesores_academicos = list(AsesorAcademico.objects.all())

        # Validamos de que existan datos base para poder crear los proyectos
        if not periodos or not asesores_academicos:
            self.stdout.write(self.style.ERROR('Error: Debes ejecutar primero los comandos de periodos y asesores.'))
            return

        # 3. DICCIONARIOS DE DATOS SEMILLA
        comunidades = [
            "Punta Cardón", "Caja de Agua", "Puerta Maravén", "Zaragoza", 
            "Las Margaritas", "Judibana", "Los Taques", "Creolandia", 
            "Santa Elena", "Bella Vista", "Punto Fijo Centro"
        ]

        temas = [
            "Desarrollo de un sistema web para el consejo comunal",
            "Mantenimiento preventivo de equipos de computación en escuela",
            "Programa de alfabetización tecnológica para adultos mayores",
            "Diseño e instalación de red local en ambulatorio",
            "Sistematización del inventario de la farmacia comunitaria",
            "Taller sobre seguridad en redes sociales para jóvenes",
            "Soporte técnico a los equipos del infocentro local"
        ]

        brigadas_creadas = 0

        # 4. BUCLE DE GENERACIÓN (30 Proyectos)
        for i in range(1, 31):
            periodo_asignado = random.choice(periodos)
            asesor_asignado = random.choice(asesores_academicos)
            comunidad_asignada = random.choice(comunidades)
            tema_asignado = random.choice(temas)
            
            # Cálculo de fechas simuladas (Inicio a partir de 2025 + días aleatorios)
            dias_aleatorios = random.randint(1, 300)
            inicio = date(2025, 1, 1) + timedelta(days=dias_aleatorios)
            # El proyecto dura entre 3 y 6 meses (90 a 180 días)
            fin = inicio + timedelta(days=random.randint(90, 180))

            # 5. CONSTRUCCIÓN DE LA RELACIÓN EN LA BASE DE DATOS
            # Paso A: Creamos la entidad Brigada (Ej: Brigada 001)
            nueva_brigada = Brigada.objects.create(
                nombre=f"{i:03d}",
                periodo=periodo_asignado
            )
            brigadas_creadas += 1

            # Paso B: Asignamos el Asesor a la Brigada usando la tabla intermedia (ManyToMany)
            BrigadaAsesor.objects.create(
                brigada=nueva_brigada,
                asesor=asesor_asignado.asesor, # Pasamos el objeto base 'Asesor'
                rol=BrigadaAsesor.Rol.ACADEMICO
            )

            # Paso C: Finalmente, creamos el Proyecto apuntando a la Brigada y al Asesor directamente
            Proyecto.objects.create(
                nombre_proyecto=f"{tema_asignado} en {comunidad_asignada}",
                comunidad=comunidad_asignada,
                fecha_inicio=inicio,
                fecha_culminacion=fin,
                aprobado=random.choices([True, False], weights=[80, 20])[0], # 80% probabilidad de estar aprobado
                brigada=nueva_brigada,
                asesor_academico=asesor_asignado
            )

        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se han creado {brigadas_creadas} brigadas con proyectos y asesores.'))