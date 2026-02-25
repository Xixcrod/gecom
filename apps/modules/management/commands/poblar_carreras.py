# apps/modules/management/commands/poblar_carreras.py
from django.core.management.base import BaseCommand
from apps.core.models import Carrera

class Command(BaseCommand):
    help = 'Puebla la base de datos con las carreras oficiales de la UNEFM'

    def handle(self, *args, **kwargs):
        Carrera.objects.all().delete()
        
        # Lista de carreras de la UNEFM
        carreras_unefm = [
            "Medicina",
            "Ciencias Veterinarias",
            "Ingeniería Civil",
            "Ingeniería Industrial",
            "Ingeniería Mecánica",
            "Ingeniería Agronómica",
            "Desarrollo Empresarial",
            "Turismo",
            "Artes Audiovisuales",
            "Educación Física, Recreación y Entrenamiento Deportivo",
            "Educación en Lengua, Literatura y Latín",
            "Educación en Ciencias Sociales",
            "PNF Enfermería",
            "PNF Fisioterapia",
            "PNF Nutrición y Dietética"
        ]
        
        for nombre in carreras_unefm:
            Carrera.objects.create(nombre_carrera=nombre)
            
        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se han creado {len(carreras_unefm)} carreras de la UNEFM.'))