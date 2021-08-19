from rest_framework.fields import SerializerMethodField
from rest_framework import serializers
from workspace.models import Workspace

class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    workspaceConfig = SerializerMethodField()

    def get_workspaceConfig(self, obj):
        return obj.workspaceconfig_set.values('acidProvider', 'storage', 'warehouseLocation', 'sparkImage', 'zeppelinInterpreterImage', 'zeppelinServerImage')[0]

    class Meta:
        model = Workspace
        fields = ["id", "name", "description", "workspaceConfig"]
