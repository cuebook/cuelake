import os
from workspace.models import (
    Workspace
)

class helperFunctions:

    def getWorkspaceName(self, workspaceId: int):
        if os.environ.get("ENVIRONMENT","") == "dev":
            workspaceHost = "localhost"
        else:
            workspaceHost = "zeppelin-server-" + Workspace.objects.get(pk=workspaceId).name
        return workspaceHost

# Export initalized class
helperFunctions = helperFunctions()