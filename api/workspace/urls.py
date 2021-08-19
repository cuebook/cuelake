from django.urls import path
from . import views

urlpatterns = [
    path("workspaces", views.Workspaces.as_view(), name="workspaces"),
    path("<int:workspaceId>", views.Workspace.as_view(), name="workspace"),
    path("workspaceConfig/<int:workspaceId>", views.WorksapceConfig.as_view(), name="workspaceConfig"),
    path("dockerimages/<str:repository>", views.DockerImages.as_view(), name="dockerimages"),
    path("createAndStartWorkspaceServer", views.CreateAndStartWorkspaceServer.as_view(), name="createAndStartWorkspaceServer"),
    path("workspaceServer/<int:workspaceId>", views.WorkspaceServer.as_view(), name="workspaceServer"),
]