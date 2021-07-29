from rest_framework import serializers
from workflows.models import Workflow, WorkflowRunLogs, WorkflowNotebookMap

class WorkflowSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    triggerWorkflow = serializers.SerializerMethodField()
    lastRun = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    notebooks = serializers.SerializerMethodField()

    def get_triggerWorkflow(self, obj):
        """
        Gets name of depends on Workflow
        """
        if not obj.triggerWorkflow:
            return None
        return {'id': obj.triggerWorkflow.id, 'name': obj.triggerWorkflow.name} 

    def get_lastRun(self, obj):
    	"""
		Gets last run time of workflow
    	"""
    	workflowRunlogs = obj.workflowrunlogs_set.order_by("-startTimestamp")
    	if workflowRunlogs.count():
    		return {
                "status": workflowRunlogs[0].status, 
                "startTimestamp": workflowRunlogs[0].startTimestamp,
                "endTimestamp": workflowRunlogs[0].endTimestamp,
                "workflowRunId": workflowRunlogs[0].id
            }
    	else:
    		return None

    def get_schedule(self, obj):
        """ Get schedule"""
        if obj.periodictask == None:
            return None
        return {'id': obj.periodictask.crontab.id, 'name': obj.periodictask.crontab.customschedule.name}

    def get_notebooks(self, obj):
        """Gets notebooks in workflow"""
        return list(WorkflowNotebookMap.objects.filter(workflow=obj).values_list("notebookId", flat=True))

    class Meta:
        model = Workflow
        fields = ["id", "name", "triggerWorkflow", "triggerWorkflowStatus", "lastRun", "schedule", "notebooks"]


class WorkflowRunLogsSerializer(serializers.ModelSerializer):
    """
    Serializer for the model WorkflowRunLogs
    """

    class Meta:
        model = WorkflowRunLogs
        fields = ["id", "status", "workflow", "startTimestamp", "endTimestamp"]
