import json
from rest_framework import serializers
# from django_celery_beat.models import CrontabSchedule
from workflows.models import Workflow, WorkflowRun, NotebookJob

class WorkflowSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    triggerWorkflow = serializers.SerializerMethodField()
    lastRun = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()

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
    	workflowRuns = obj.workflowrun_set.order_by("-startTimestamp")
    	if workflowRuns.count():
    		return workflowRuns[0].startTimestamp
    	else:
    		return None

    def get_schedule(self, obj):
        """ Get schedule"""
        if not obj.crontab:
            return None
        return {'id': obj.crontab.id, 'name': str(obj.crontab)}

    class Meta:
        model = Workflow
        fields = ["id", "name", "triggerWorkflow", "triggerWorkflowStatus", "lastRun", "schedule"]


class WorkflowRunSerializer(serializers.ModelSerializer):
    """
    Serializer for the model WorkflowRun
    """

    class Meta:
        model = WorkflowRun
        fields = ["id", "status", "workflow", "startTimestamp", "endTimestamp"]


# class RunStatusSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the model RunStatus
#     """
#     logsJSON = serializers.SerializerMethodField()
    
#     def get_logsJSON(self, obj):
#         """
#         Gets logs in JSON form
#         """
#         return json.loads(obj.logs)

#     class Meta:
#         model = RunStatus
#         fields = ["id", "notebookId", "startTimestamp", "status", "logsJSON", "runType"]
