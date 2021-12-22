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
        deployments = Kubernetes.getDeployments()
        runningDeployments = {}
        for deployment in deployments:
            if deployment.status.replicas > 0 and deployment.metadata.name.startswith("zeppelin-server-"):
                runningDeployments[deployment.metadata.name[16:]] = deployment
        workspaces = Workspace.objects.all()
        data = WorkspaceSerializer(workspaces, many=True).data
        for workspace in data:
            runningDeployment = runningDeployments.get(workspace["name"], False)
            if runningDeployment:
                workspace['replica'] = runningDeployment.status.replicas
            else:
                workspace['replica'] = 0
        res.update(True, "Workspaces retrieved successfully", data)
        return res

    @staticmethod
    def switchWorkspaceServer(workspaceId: int):
        res = ApiResponse(message="Error switching workspace")
        Kubernetes.switchWorkspaceServer(workspaceId)
        res.update(True, "Workspace switched successfully")
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
    def startWorkspaceServer(workspaceId: int, isNew: bool = False):
        workspaceName = Workspace.objects.get(pk=workspaceId).name
        workspaceConfigDict = WorkspaceConfig.objects.get(workspace_id=workspaceId).__dict__
        res = ApiResponse(message="Error starting workspace server")
        Kubernetes.addZeppelinServer(workspaceName, workspaceConfigDict, isNew)
        res.update(True, message="Workspace started successfully")
        return res

    @staticmethod
    def stopWorkspaceServer(workspaceId: int):
        workspaceName = Workspace.objects.get(pk=workspaceId).name
        res = ApiResponse(message="Error stopping workspace")
        Kubernetes.removeWorkspace(workspaceName)
        res.update(True, "Workspace stopped successfully")
        return res

    @staticmethod
    def deleteWorkspace(workspaceId: int):
        workspaceName = Workspace.objects.get(pk=workspaceId).name
        workspace = Workspace.objects.get(pk=workspaceId)
        workspace.delete()
        res = ApiResponse(message="Error deleting workspace server")
        Kubernetes.removeWorkspace(workspaceName)
        res.update(True, message="Workspace deleted successfully")
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
        WorkspaceService.startWorkspaceServer(workspace.id, True)
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
