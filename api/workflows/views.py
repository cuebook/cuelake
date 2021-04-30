from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from workflows.services import WorkflowServices, WorkflowActions

class Workflows(APIView):
    """
    Class to get and post workflows 
    """
    def get(self, request, offset: int):
        """Gets all workflows"""
        res = WorkflowServices.getWorkflows(offset)
        return Response(res.json())

    def post(self, request):
        data = request.data

        name = data.get("name", "")
        scheduleId = data.get("scheduleId", "")
        triggerWorkflowId = data.get("triggerWorkflowId", "")
        triggerWorkflowStatus = data.get("triggerWorkflowStatus", "")
        notebookIds = data.get("notebookIds", [])

        if 'id' in data and data['id']:
            res = WorkflowServices.updateWorkflow(data['id'], name, scheduleId, triggerWorkflowId, triggerWorkflowStatus, notebookIds)
        else:
            res = WorkflowServices.createWorkflow(name, scheduleId, triggerWorkflowId, triggerWorkflowStatus, notebookIds)
        return Response(res.json())

    # def delete(self, request, notebookId):
    #     res = NotebookJobServices.deleteNotebook(notebookId)
    #     return Response(res.json())


class WorkflowRun(APIView):
    """
    Class to get and post WorkflowRun
    """
    def get(self, request, workflowId: int, offset: int):
        """Gets all workflows runs associated with given workflow
        :param workflowId: id of Workflows.Workflow
        """
        res = WorkflowServices.getWorkflowRuns(workflowId, offset)
        return Response(res.json())


class RunWorkflow(APIView):
    """
    Class to manually run workflows
    """
    def get(self, request, workflowId: int):
        """Gets all workflows runs associated with given workflow
        :param workflowId: id of Workflows.Workflow
        """
        res = WorkflowActions.runWorkflow(workflowId)
        return Response(res.json())


class StopWorkflow(APIView):
    """
    Class to manually stop workflows
    """
    def get(self, request, workflowId: int):
        """Gets all workflows runs associated with given workflow
        :param workflowId: id of Workflows.Workflow
        """
        res = WorkflowActions.stopWorkflow(workflowId)
        return Response(res.json())


class WorkflowRunLog(APIView):
    """
    Class to get and post WorkflowRun
    """
    def get(self, request, workflowId: int):
        """Gets all workflows runs associated with given workflow
        :param workflowId: id of Workflows.Workflow
        """
        res = WorkflowServices.getWorkflowRunLogs(workflowId)
        return Response(res.json())


class UpdateTriggerWorkflow(APIView):
    """
    Class to update trigger workflow associated with workflow
    """
    def post(self, request, workflowId: int):
        """
        Updated trigger workflow
        """
        data = request.data
        triggerWorkflowId = data.get("triggerWorkflowId", "")
        triggerWorkflowStatus = data.get("triggerWorkflowStatus", "")
        res = WorkflowServices.updateTriggerWorkflow(workflowId, triggerWorkflowId, triggerWorkflowStatus)
        return Response(res.json())


class UpdateSchedule(APIView):
    """
    Class to update schedule associated with workflow
    """
    def post(self, request, workflowId: int):
        """
        Updated trigger workflow
        """
        data = request.data
        scheduleId = data.get("scheduleId", "")
        res = WorkflowServices.updateSchedule(workflowId, scheduleId)
        return Response(res.json())

