import uuid
from django.db import models

# --- MODELOS BASE ---

class Periodo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Carrera(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_carrera = models.CharField(max_length=200)
    icono = models.ImageField(upload_to='carreras/iconos/', blank=True, null=True)

    def __str__(self):
        return self.nombre_carrera

class Asesor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

# --- HERENCIA DE ASESORES ---
# Nota: En herencia multi-tabla, el OneToOneField actúa como PK, por lo que hereda el UUID de Asesor.

class AsesorComunitario(models.Model):
    asesor = models.OneToOneField(Asesor, on_delete=models.CASCADE, primary_key=True)
    
    def __str__(self):
        return f"Comunitario: {self.asesor.nombres}"

class AsesorAcademico(models.Model):
    asesor = models.OneToOneField(Asesor, on_delete=models.CASCADE, primary_key=True)
    profesion = models.CharField(max_length=100)
    dependencia = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Académico: {self.asesor.nombres}"

# --- ESTRUCTURA PRINCIPAL ---

class Brigada(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='brigadas')
    asesores = models.ManyToManyField(Asesor, through='BrigadaAsesor')

    def __str__(self):
        return self.nombre

class BrigadaAsesor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Rol(models.TextChoices):
        ACADEMICO = 'ACADEMICO', 'Académico'
        COMUNITARIO = 'COMUNITARIO', 'Comunitario'

    brigada = models.ForeignKey(Brigada, on_delete=models.CASCADE)
    asesor = models.ForeignKey(Asesor, on_delete=models.CASCADE)
    
    rol = models.CharField(
        max_length=20, 
        choices=Rol.choices, 
        default=Rol.COMUNITARIO
    )

    def __str__(self):
        return f"{self.asesor} - {self.brigada} ({self.get_rol_display()})"

class Proyecto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_proyecto = models.CharField(max_length=255)
    comunidad = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_culminacion = models.DateField(null=True, blank=True)
    aprobado = models.BooleanField(default=False)
    
    brigada = models.ForeignKey(Brigada, on_delete=models.CASCADE, related_name='proyectos')
    
    asesor_academico = models.ForeignKey(
        AsesorAcademico, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='proyectos_asignados'
    )
    
    constancia_asesor = models.FileField(upload_to='asesores/constancias/', blank=True, null=True)
    certificado_asesor = models.FileField(upload_to='asesores/certificados/', blank=True, null=True)

    def __str__(self):
        return self.nombre_proyecto

class GrupoDocumentos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    planilla_inscripcion = models.FileField(upload_to='proyectos/planillas/', blank=True, null=True)
    control_horas = models.FileField(upload_to='proyectos/horas/', blank=True, null=True)
    anteproyecto = models.FileField(upload_to='proyectos/anteproyectos/', blank=True, null=True)
    informe_final = models.FileField(upload_to='proyectos/informes/', blank=True, null=True)
    
    proyecto = models.OneToOneField(Proyecto, on_delete=models.CASCADE, related_name='documentos')

    def __str__(self):
        return f"Docs de: {self.proyecto}"

# --- ESTUDIANTES ---

class Estudiante(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    
    brigada = models.ForeignKey(Brigada, on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, related_name='estudiantes')

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Certificado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha_retiro = models.DateField(null=True, blank=True)
    fecha_actualizacion = models.DateField(auto_now=True)
    archivo = models.FileField(upload_to='estudiantes/certificados/', blank=True, null=True)
    
    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='certificado')

    def __str__(self):
        return f"Certificado: {self.estudiante}"