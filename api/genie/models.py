from django.db import models
from django_celery_beat.models import PeriodicTask

# Create your models here.

class NotebookJob(PeriodicTask):
    """
    Model class for a single job to be run on a single notebook
    """
    notebookId = models.CharField(max_length=50, db_index=True)
    notebookName = models.CharField(max_length=100)