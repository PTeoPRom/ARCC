from django.db import models

# Create your models here.
class ReportData(models.Model):
    case_id = models.IntegerField()  # Identificador del caso
    processes_report = models.TextField()  # Reporte de procesos en ejecución
    security_events_report = models.TextField()  # Reporte de eventos de seguridad recientes
    startup_programs_report = models.TextField()  # Reporte de programas de inicio automático
    recent_files_report = models.TextField()  # Reporte de archivos modificados recientemente
    scheduled_tasks_report = models.TextField()  # Reporte de tareas programadas en el sistema
    registry_keys_report = models.TextField()  # Reporte de claves de registro sospechosas
    network_connections_report = models.TextField()  # Reporte de conexiones de red activas
    executive_report = models.TextField() # Reporte ejecutivo para rapida comprensión
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación del reporte

    