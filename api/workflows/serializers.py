import json
from rest_framework import serializers
# from django_celery_beat.models import CrontabSchedule
from workflows.models import Workflow, WorkflowRun, NotebookJob

class WorkflowSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    dependsOnWorkflow = serializers.SerializerMethodField()
    lastRun = serializers.SerializerMethodField()

    def get_dependsOnWorkflow(self, obj):
        """
        Gets name of depends on Workflow
        """
        return obj.dependsOnWorkflow.name if obj.dependsOnWorkflow else None

    def get_lastRun(self, obj):
    	"""
		Gets last run time of workflow
    	"""
    	workflowRuns = obj.workflowrun_set.order_by("-startTimestamp")
    	if workflowRuns.count():
    		return workflowRuns[0].startTimestamp
    	else:
    		return None

    class Meta:
        model = Workflow
        fields = ["id", "name", "dependsOnWorkflow", "dependsOnWorkflowStatus", "lastRun"]


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
