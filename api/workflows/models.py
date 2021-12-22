from django.db import models
from django_celery_beat.models import PeriodicTask
from workspace.models import Workspace

STATUS_SUCCESS = "SUCCESS"
STATUS_ERROR = "ERROR"
STATUS_ALWAYS = "ALWAYS"
STATUS_RUNNING = "RUNNING"
STATUS_QUEUED = "QUEUED"
STATUS_ABORTED = "ABORTED"


class Workflow(models.Model):
	name = models.CharField(max_length=200, default="")
	periodictask = models.ForeignKey(PeriodicTask, on_delete=models.SET_NULL, null=True)
	triggerWorkflow = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
	triggerWorkflowStatus = models.CharField(max_length=50, default=STATUS_SUCCESS)
	workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE,null=True, default=None)

class WorkflowRunLogs(models.Model):
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_index=True)
	status = models.CharField(max_length=50, default=STATUS_SUCCESS)
	startTimestamp = models.DateTimeField(auto_now_add=True)
	endTimestamp = models.DateTimeField(null=True, default=None)
	taskId = models.CharField(max_length=200, default="")

class WorkflowNotebookMap(models.Model):
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_index=True)
	notebookId = models.CharField(max_length=20, default="000000000")
