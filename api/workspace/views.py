from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from workspace.services import WorkspaceService

class Workspaces(APIView):
    def get(self, request):
        res = WorkspaceService.getWorkspaces()
        return Response(res.json())

    def post(self, request):
        data = request.data
        name = data.get("name", False)
        description = data.get("description", False)
        res = WorkspaceService.createWorkspace(name, description)
        return Response(res.json())


class Workspace(APIView):
    def get(self, request, workspaceId: int):
        res = WorkspaceService.getWorkspace(workspaceId)
        return Response(res.json())


class WorksapceConfig(APIView):
    def put(self, request):
        workspaceConfigDict = request.data
        res = WorkspaceService.updateWorkspaceConfig(workspaceConfigDict)
        return Response(res.json())