from django.db import models

# Create your models here.
class AgentData(models.Model):
    case_id = models.IntegerField()  # Identificador del caso
    users = models.JSONField()  # Lista de usuarios del sistema
    network_connections = models.JSONField()  # Conexiones de red activas
    processes = models.JSONField()  # Procesos en ejecución
    security_events = models.JSONField()  # Eventos de seguridad recientes
    startup_programs = models.JSONField()  # Programas de inicio automático
    recent_files = models.JSONField()  # Archivos modificados recientemente
    scheduled_tasks = models.JSONField()  # Tareas programadas en el sistema
    registry_keys = models.JSONField()  # Claves de registro sospechosas