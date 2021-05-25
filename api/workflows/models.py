from django.db import models
from django_celery_beat.models import PeriodicTask, PeriodicTasks
from django.db.models import signals

STATUS_SUCCESS = "SUCCESS"
STATUS_ERROR = "ERROR"
STATUS_ALWAYS = "ALWAYS"
STATUS_RUNNING = "RUNNING"
STATUS_RECEIVED = "RECEIVED" 		# just before triggering job
STATUS_ABORTED = "ABORTED"


class Workflow(PeriodicTask):
	"""
	Subclass of django_celery_beat.models.PeriodicTask
	"""
	triggerWorkflow = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, db_index=True)
	triggerWorkflowStatus = models.CharField(max_length=50, default=STATUS_SUCCESS)

class WorkflowRun(models.Model):
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_index=True)
	status = models.CharField(max_length=50, default=STATUS_SUCCESS)
	startTimestamp = models.DateTimeField(auto_now_add=True)
	endTimestamp = models.DateTimeField(null=True, default=None)
	taskId = models.CharField(max_length=200, default="")

class NotebookJob(models.Model):
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_index=True)
	notebookId = models.CharField(max_length=20, default="000000000")


signals.pre_delete.connect(PeriodicTasks.changed, sender=Workflow)
signals.pre_save.connect(PeriodicTasks.changed, sender=Workflow)
