from workspace.models import (
    Workspace,
    WorkspaceConfig
)
from workspace.serializers import WorkspaceSerializer
from utils.apiResponse import ApiResponse

class WorkspaceService:
    """
    Class containing services related to NotebookJob model
    """

    @staticmethod
    def getWorkspaces():
        """
        Service to fetch and serialize Workflows
        :param offset: Offset for fetching NotebookJob objects
        """
        res = ApiResponse(message="Error retrieving workflows")
        workspaces = Workspace.objects.all()   
        data = WorkspaceSerializer(workspaces, many=True).data
        res.update(True, "Worksapces retrieved successfully", data)
        return res

    def createWorkspace(name: str, description: str):
        res = ApiResponse(message="Error creating workspace")
        workspace = Workspace.objects.create(name=name, description=description)
        WorkspaceConfig.objects.create(workspace=workspace)
        res.update(True, "Workspace created successfully")
        return res

    def updateWorkspaceConfig(workspaceId: int, workspaceConfigDict: dict):
        res = ApiResponse(message="Error updating config of workspace")
        worksapceConfig = WorkspaceConfig.objects.get(workspace_id=workspaceId)
        worksapceConfig.update(**workspaceConfigDict)
        res.update(True, message="Successfully updated workspace config")
        return res

    def startWorksapceServer(workspaceId: int):
        res = ApiResponse(message="Error creating worksapce server")
        return res

    @staticmethod
    def getWorkspace():
        """
        Service to fetch and serialize Workflows
        :param offset: Offset for fetching NotebookJob objects
        """
        res = ApiResponse(message="Error retrieving workflows")
        workspaces = Workspace.objects.all()        
        total = workspaces.count()
        return res
