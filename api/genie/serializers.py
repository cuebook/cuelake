from rest_framework import serializers
from genie.models import NotebookJob

class NotebookJobSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    class Meta:
        model = NotebookJob
        fields = ["id", "notebookId", "notebookName"]