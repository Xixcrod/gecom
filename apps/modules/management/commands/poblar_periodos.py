# apps/modules/management/commands/poblar_periodos.py
from django.core.management.base import BaseCommand
from apps.core.models import Periodo

class Command(BaseCommand):
    help = 'Puebla la base de datos con combinaciones reales de periodos de servicio comunitario'

    def handle(self, *args, **kwargs):
        # Limpiamos los periodos existentes para evitar duplicados
        Periodo.objects.all().delete()
        
        periodos_creados = 0
        
        for anio in range(2000, 2027):
            # 1. Duración de un solo semestre (Primer semestre)
            Periodo.objects.create(nombre=f"I-{anio}-I-{anio}")
            
            # 2. Duración de dos semestres (Dentro del mismo año)
            Periodo.objects.create(nombre=f"I-{anio}-II-{anio}")
            
            # 3. Duración de un solo semestre (Segundo semestre)
            Periodo.objects.create(nombre=f"II-{anio}-II-{anio}")
            
            # 4. Duración de dos semestres (Cruzando de año, ej: II-2025-I-2026)
            Periodo.objects.create(nombre=f"II-{anio}-I-{anio+1}")
            
            periodos_creados += 4
            
        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se han creado {periodos_creados} periodos realistas.'))