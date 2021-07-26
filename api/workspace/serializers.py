from rest_framework import serializers
from workspace.models import Workspace

class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    class Meta:
        model = Workspace
        fields = ["id", "name", "description"]
