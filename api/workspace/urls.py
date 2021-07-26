from django.urls import path
from . import views

urlpatterns = [
    path("workspaces", views.Workspaces.as_view(), name="workspaces"),
    path("workspace/<int:workspaceId>", views.Workspace.as_view(), name="workspace"),
]