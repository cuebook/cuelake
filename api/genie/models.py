from attr import make_class
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
    timestamp = models.DateTimeField(auto_now_add=True)
    notebookJob = models.ForeignKey(NotebookJob, on_delete=models.CASCADE)
    logs = models.TextField(default="{}") # Should be valid JSON
    status = models.CharField(max_length=7)