import json
from rest_framework import serializers
from django_celery_beat.models import CrontabSchedule
from genie.models import NotebookJob, RunStatus

class NotebookJobSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    class Meta:
        model = NotebookJob
        fields = ["id", "notebookId"]

class RunStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for the model RunStatus
    """
    logsJSON = serializers.SerializerMethodField()
    
    def get_logsJSON(self, obj):
        """
        Gets logs in JSON form
        """
        return json.loads(obj.logs)

    class Meta:
        model = RunStatus
        fields = ["id", "notebookJob", "timestamp", "status", "logsJSON"]

class CrontabScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for the model CrontabSchedule
    """
    schedule = serializers.SerializerMethodField()

    def get_schedule(self, obj):
        """
        Gets string form of the crontab
        """
        return str(obj)
    
    class Meta:
        model = CrontabSchedule
        fields = ["id", "schedule"]