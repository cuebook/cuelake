from django.urls import path
from . import views

urlpatterns = [
    path("workflows/<int:offset>", views.Workflows.as_view(), name="workflows"),
    path("workflow/<int:workflowId>", views.Workflow.as_view(), name="workflow"),
    path("workflows", views.Workflows.as_view(), name="workflowsPost"),
    path("workflowRuns/<int:workflowId>/<int:offset>", views.WorkflowRun.as_view(), name="workflowRuns"),
    path("workflowRuns/<int:workflowRunId>", views.WorkflowRunLog.as_view(), name="workflowRunLogs"),
    path("runWorkflow/<int:workflowId>", views.RunWorkflow.as_view(), name="runWorkflow"),
    path("stopWorkflow/<int:workflowId>", views.StopWorkflow.as_view(), name="stopWorkflow"),
    path("updateTriggerWorkflow/<int:workflowId>", views.UpdateTriggerWorkflow.as_view(), name="updateTriggerWorkflow"),
    path("updateSchedule/<int:workflowId>", views.UpdateSchedule.as_view(), name="updateSchedule"),
]