from django.db import models
from django_celery_beat.models import PeriodicTask

STATUS_SUCCESS = "success"
STATUS_FAILURE = "failure"
STATUS_ALWAYS = "always"


class Workflow(PeriodicTask):
	"""
	Subclass of django_celery_beat.models.PeriodicTask
	"""
	dependsOnWorkflow = models.ForeignKey("self", on_delete=models.CASCADE, db_index=True)
	dependsOnWorkflowStatus = models.CharField(max_length=50, default=STATUS_SUCCESS)

class WorkflowRun(models.Model):
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_index=True)
	status = models.CharField(max_length=50, default=STATUS_SUCCESS)
	startTimestamp = models.DateTimeField(auto_now_add=True)
	endTimestamp = models.DateTimeField(null=True, default=None)

class NotebookJob(models.Model):
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_index=True)
	notebookId = models.CharField(max_length=20, default="000000000")
	# dependsOn notebookId = models.CharField(max_length=20, default="000000000")
	# dependsOn notebookStatus = 

