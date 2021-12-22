from django.db import models
from django.db.models.fields import CharField
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule
from workflows.models import WorkflowRunLogs
from django.db.models import signals
from workspace.models import Workspace


NOTEBOOK_STATUS_SUCCESS = "SUCCESS"
NOTEBOOK_STATUS_ERROR = "ERROR"
NOTEBOOK_STATUS_RUNNING = "RUNNING"
NOTEBOOK_STATUS_FINISHED = "FINISHED"
NOTEBOOK_STATUS_ABORT = "ABORT"
NOTEBOOK_STATUS_QUEUED = "QUEUED"


class NotebookJob(PeriodicTask):
    """
    Model class for a single job to be run on a single notebook
    Subclass of django_celery_beat.models.PeriodicTask
    """
    notebookId = models.CharField(max_length=50, db_index=True, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE,null=True, default=None)

class NotebookRunLogs(models.Model):
    """
    Model class to store logs and statuses of NotebookJob runs
    """
    startTimestamp = models.DateTimeField(auto_now_add=True)
    endTimestamp = models.DateTimeField(null=True, default=None)
    updateTimestamp = models.DateTimeField(auto_now=True)
    notebookId = models.CharField(max_length=20, default="000000000")
    logs = models.TextField(default="{}") # Should be valid JSON
    status = models.CharField(max_length=20)
    runType = models.CharField(max_length=20, blank=True, null=True) # Manual/Scheduled
    message = models.CharField(max_length=5000, null=True, default=None)
    workflowRunLogs = models.ForeignKey(WorkflowRunLogs, null=True, blank=True, on_delete=models.SET_NULL)
    taskId = models.CharField(max_length=200, default="")
    zeppelinServerId = models.CharField(max_length=200, default="")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE,null=True, default=None)


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
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE,null=True, default=None)

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

class CustomSchedule(CrontabSchedule):
    name = models.CharField(max_length=200, blank=True, null=True)

class NotebookObject(models.Model):
    notebookZeppelinId = models.CharField(max_length=10)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, blank=True, null=True)
    notebookTemplate = models.ForeignKey(NotebookTemplate, on_delete=models.CASCADE)
    defaultPayload = models.JSONField(default={})


signals.pre_delete.connect(PeriodicTasks.changed, sender=NotebookJob)
signals.pre_save.connect(PeriodicTasks.changed, sender=NotebookJob)
signals.pre_delete.connect(PeriodicTasks.changed, sender=PeriodicTask)
signals.pre_save.connect(PeriodicTasks.changed, sender=PeriodicTask)
signals.post_delete.connect(
    PeriodicTasks.update_changed, sender=CrontabSchedule)
signals.post_save.connect(
    PeriodicTasks.update_changed, sender=CrontabSchedule)
signals.post_delete.connect(
    PeriodicTasks.update_changed, sender=CustomSchedule)
signals.post_save.connect(
    PeriodicTasks.update_changed, sender=CustomSchedule)