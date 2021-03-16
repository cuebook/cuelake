from rest_framework import serializers
from django_celery_beat.models import CrontabSchedule
from genie.models import NotebookJob

class NotebookJobSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    class Meta:
        model = NotebookJob
        fields = ["id", "notebookId"]


class CrontabScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for the model CrontabSchedule
    """
    schedule = serializers.SerializerMethodField()

    def get_schedule(self, obj):
        """Gets star count"""
        return str(obj)
    
    class Meta:
        model = CrontabSchedule
        fields = ["id", "schedule"]