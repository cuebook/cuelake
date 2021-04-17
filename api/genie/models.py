from django.db import models
from django_celery_beat.models import PeriodicTask

class NotebookJob(PeriodicTask):
    """
    Model class for a single job to be run on a single notebook
    Subclass of django_celery_beat.models.PeriodicTask
    """
    notebookId = models.CharField(max_length=50, db_index=True, unique=True)

class RunStatus(models.Model):
    """
    Model class to store logs and statuses of NotebookJob runs
    """
    startTimestamp = models.DateTimeField(auto_now_add=True)
    endTimestamp = models.DateTimeField(null=True, default=None)
    notebookId = models.CharField(max_length=20, default="000000000")
    logs = models.TextField(default="{}") # Should be valid JSON
    status = models.CharField(max_length=20)
    runType = models.CharField(max_length=20, blank=True, null=True) # Manual/Scheduled
    message = models.CharField(max_length=5000, null=True, default=None)


# Connection Models
class ConnectionType(models.Model):
    name = models.CharField(max_length=200, db_index=True, unique=True)
    def __str__(self):
        return self.name


# eg. host, username, password
class ConnectionParam(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    label = models.CharField(max_length=200, blank=True, null=True)
    isEncrypted = models.BooleanField(default=False)
    connectionType = models.ForeignKey(
        ConnectionType, on_delete=models.CASCADE, db_index=True, related_name="connectionTypeParam"
    )
    properties = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.connectionType.name


class Connection(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    connectionType = models.ForeignKey(
        ConnectionType, on_delete=models.CASCADE, db_index=True, related_name="connectionTypeConnection"
    )

    def __str__(self):
        return self.name

class ConnectionParamValue(models.Model):
    connectionParam = models.ForeignKey(ConnectionParam, on_delete=models.CASCADE, related_name="cpvcp")
    value = models.TextField()
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name="cpvc")

# Notebook template model
class NotebookTemplate(models.Model):
    template = models.JSONField(default={})
    formJson = models.JSONField(default={})
    name = models.CharField(max_length=200, blank=True, null=True)