import asyncio
import json
import pytz
import time
from workflows.models import Workflow, WorkflowRun, NotebookJob
from workflows.serializers import WorkflowSerializer, WorkflowRunSerializer
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import Zeppelin

# from genie.tasks import runNotebookJob as runNotebookJobTask

# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"


class WorkflowServices:
    """
    Class containing services related to NotebookJob model
    """

    @staticmethod
    def getWorkflows(offset: int = 0):
        """
        Service to fetch and serialize Workflows
        :param offset: Offset for fetching NotebookJob objects
        """
        LIMIT = 10
        res = ApiResponse(message="Error retrieving workflows")
        workflows = Workflow.objects.filter(enabled=True).order_by("-id")
        total = workflows.count()
        data = WorkflowSerializer(workflows[offset:LIMIT], many=True).data

        res.update(
            True,
            "Workflows retrieved successfully",
            {"total": total, "workflows": data},
        )
        return res

    @staticmethod
    def createWorkflow(
        name: str, schedule: int, triggerWorkflowId: int, triggerWorkflowStatus: str
    ):
        """
        Creates workflow
        :param name: name of new workflow
        :param schedule: crontab id
        :param triggerWorkflowId: id of workflow which triggers this workflow
        :param triggerWorkflowStatus: ["success", "failure", "always"] required
                status of triggerWorkflow to trigger this workflow
        """
        res = ApiResponse(message="Error in creating workflow")
        workflow = Workflow.objects.create(
            name=name,
            crontab_id=schedule,
            triggerWorkflow_id=triggerWorkflowId,
            triggerWorkflowStatus=triggerWorkflowStatus,
        )
        res.update(True, "Workflow created successfully", workflow.id)
        return res

    @staticmethod
    def updateWorkflow(
        id: int,
        name: str,
        schedule: int,
        triggerWorkflowId: int,
        triggerWorkflowStatus: str,
    ):
        """
        Updates workflow
        :param name: name of new workflow
        :param schedule: crontab id
        :param triggerWorkflowId: id of workflow which triggers this workflow
        :param triggerWorkflowStatus: ["success", "failure", "always"] required
                status of triggerWorkflow to trigger this workflow
        """
        res = ApiResponse(message="Error in updating workflow")
        workflow = Workflow.objects.filter(id=id).update(
            name=name,
            crontab_id=schedule,
            triggerWorkflow_id=triggerWorkflowId,
            triggerWorkflowStatus=triggerWorkflowStatus,
        )
        try:
            if workflow:
                res.update(True, "Workflow updated successfully", workflow)
        except:
            res.update(False, "Error in updating workflow")
        return res

    @staticmethod
    def getWorkflowRuns(workflowId: int, offset: int):
        """
        Service to fetch and serialize workflows runs
        :param workflowId: id of Workflows.Workflow
        """
        LIMIT = 10
        res = ApiResponse(message="Error in retrieving workflow logs")
        workflowRuns = WorkflowRun.objects.filter(workflow=workflowId).order_by("-id")
        total = workflowRuns.count()
        data = WorkflowRunSerializer(workflowRuns[offset:LIMIT], many=True).data

        res.update(
            True,
            "WorkflowRuns retrieved successfully",
            {"total": total, "workflowRuns": data},
        )
        return res

    @staticmethod
    def getWorkflowRunLogs(workflowRunId: int):
        """
        Service to fetch logs related to given workflowRun
        :param workflowRunId: if of model workflows.workflowRun
        """
        res = ApiResponse(message="Error in retrieving workflow logs")
        workflowRun = WorkflowRun.objects.get(id=workflowRunId)
        total = []
        res.update(
            True,
            "WorkflowRuns retrieved successfully",
            {"total": total, "workflowRunLogs": []},
        )
        return res

    # @staticmethod
    # def addNotebook(payload):
    #     res = ApiResponse(message="Error adding notebook")
    #     notebookTemplate = NotebookTemplate.objects.get(id=payload.get("notebookTemplateId", 0))
    #     context = payload # Storing payload in context variable so that it can be used for rendering
    #     # Handling connection variables
    #     if payload.get("sourceConnection", False):
    #         connection = Connection.objects.get(id=payload["sourceConnection"])
    #         connectionParams = connection.cpvc.all()
    #         for cp in connectionParams:
    #             paramName = cp.connectionParam.name
    #             context["sourceConnection_" + paramName] = cp.value
    #     if payload.get("targetConnection", False):
    #         connection = Connection.objects.get(id=payload["sourceConnection"])
    #         connectionParams = connection.cpvc.all()
    #         for cp in connectionParams:
    #             paramName = cp.connectionParam.name
    #             context["sourceConnection_" + paramName] = cp.value
    #     # Handling S3 path - Splitting it to get the table name
    #     if payload.get("destinationTableS3Path", False):
    #         destinationTableName = payload["destinationTableS3Path"].rsplit('/', 1)[1]
    #         warehouseLocation = payload["destinationTableS3Path"].rsplit('/', 1)[0]
    #         context["destinationTableName"] = destinationTableName
    #         context["warehouseLocation"] = warehouseLocation
    #     # Adding a temp table name to the context
    #     context["tempTableName"] = "tempTable_" + str(round(time.time() * 1000))
    #     notebook = Template(notebookTemplate.template).render(Context(context))
    #     response = Zeppelin.addNotebook(notebook)
    #     if response:
    #         res.update(True, "Notebook added successfully")
    #     return res
