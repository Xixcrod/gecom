# apps/modules/management/commands/poblar_periodos.py
from django.core.management.base import BaseCommand
from apps.core.models import Periodo

class Command(BaseCommand):
    # Descripción que aparecerá al ejecutar `python manage.py help`
    help = 'Puebla la base de datos con combinaciones reales de periodos de servicio comunitario'

    def handle(self, *args, **kwargs):
        # 1. LIMPIEZA INICIAL: 
        # Borramos todos los periodos existentes antes de poblar para evitar 
        # duplicados si el comando se ejecuta múltiples veces.
        Periodo.objects.all().delete()
        
        periodos_creados = 0
        
        # 2. GENERACIÓN DE DATOS (Años 2000 al 2026):
        for anio in range(2000, 2027):
            # Para cada año, generamos las 4 combinaciones lógicas de tiempo
            # que puede durar un proyecto de servicio comunitario:
            
            # Caso A: El proyecto dura solo el primer semestre del año
            Periodo.objects.create(nombre=f"I-{anio}-I-{anio}")
            
            # Caso B: El proyecto dura todo el año (inicia en I y termina en II)
            Periodo.objects.create(nombre=f"I-{anio}-II-{anio}")
            
            # Caso C: El proyecto dura solo el segundo semestre del año
            Periodo.objects.create(nombre=f"II-{anio}-II-{anio}")
            
            # Caso D: El proyecto cruza de año (inicia a finales de un año y termina a inicios del siguiente)
            Periodo.objects.create(nombre=f"II-{anio}-I-{anio+1}")
            
            periodos_creados += 4
            
        # 3. FEEDBACK POR CONSOLA
        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se han creado {periodos_creados} periodos realistas.'))