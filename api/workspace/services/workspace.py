from django.db import transaction
from utils.dockerHubAPI import DockerHubAPI
from workspace.models import (
    Workspace,
    WorkspaceConfig
)
from workspace.serializers import WorkspaceSerializer
from utils.apiResponse import ApiResponse
from utils.dockerHubAPI import dockerHubAPI
from utils.kubernetesAPI import Kubernetes

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

    @staticmethod
    def createWorkspace(name: str, description: str):
        res = ApiResponse(message="Error creating workspace")
        workspace = Workspace.objects.create(name=name, description=description)
        WorkspaceConfig.objects.create(workspace=workspace)
        res.update(True, "Workspace created successfully")
        return res

    @staticmethod
    def updateWorkspaceConfig(workspaceId: int, workspaceConfigDict: dict):
        res = ApiResponse(message="Error updating config of workspace")
        worksapceConfig = WorkspaceConfig.objects.get(workspace_id=workspaceId)
        for (key, value) in workspaceConfigDict.items():
            setattr(worksapceConfig, key, value)
        worksapceConfig.save()
        res.update(True, message="Successfully updated workspace config")
        return res

    @staticmethod
    def startWorksapceServer(workspace: Workspace):
        res = ApiResponse(message="Error creating worksapce server")
        workspaceName = workspace.name
        workspaceConfigDict = WorkspaceConfig.objects.get(workspace=workspace).__dict__
        Kubernetes.addZeppelinServer(workspaceName, workspaceConfigDict)
        return res

    @staticmethod
    @transaction.atomic
    def createAndStartWorkspaceServer(workspaceDict: dict, workspaceConfigDict: dict):
        res = ApiResponse(message="Error creating workspace")
        workspace = Workspace.objects.create(**workspaceDict)
        WorkspaceConfig.objects.create(workspace=workspace)
        worksapceConfig = WorkspaceConfig.objects.get(workspace_id=workspace.id)
        for (key, value) in workspaceConfigDict.items():
            setattr(worksapceConfig, key, value)
        worksapceConfig.save()
        WorkspaceService.startWorksapceServer(workspace)
        res.update(True, message="Successfully created workspace config")
        return res

    @staticmethod
    def getDockerImages(repository: str):
        res = ApiResponse(message="Error fetching docker images")
        imageTags = dockerHubAPI.getImageTags(repository)
        res.update(True, message="Image tags fetched successfully", data=imageTags)
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
