from typing import List
import asyncio
import json
import pytz
import time
from django.db import transaction
import polling
from workflows.models import (
    Workflow,
    WorkflowRun,
    NotebookJob,
    STATUS_SUCCESS,
    STATUS_FAILURE,
    STATUS_ALWAYS,
    STATUS_RUNNING,
    STATUS_RECEIVED,
)
from workflows.serializers import WorkflowSerializer, WorkflowRunSerializer
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import Zeppelin

from genie.tasks import runNotebookJob as runNotebookJobTask
from genie.models import RunStatus, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_SUCCESS

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
    @transaction.atomic
    def createWorkflow(
        name: str,
        scheduleId: int,
        triggerWorkflowId: int,
        triggerWorkflowStatus: str,
        notebookIds: List[int],
    ):
        """
        Creates workflow
        :param name: name of new workflow
        :param scheduleId: crontab id
        :param triggerWorkflowId: id of workflow which triggers this workflow
        :param triggerWorkflowStatus: ["success", "failure", "always"] required
                status of triggerWorkflow to trigger this workflow
        :param notebookIds: notebookIds for workflow
        """
        res = ApiResponse(message="Error in creating workflow")
        workflow = Workflow.objects.create(
            name=name,
            crontab_id=scheduleId,
            triggerWorkflow_id=triggerWorkflowId,
            triggerWorkflowStatus=triggerWorkflowStatus,
        )
        notebookJobs = [
            NotebookJob(workflow=workflow, notebookId=notebookId)
            for notebookId in notebookIds
        ]
        NotebookJob.objects.bulk_create(notebookJobs)

        res.update(True, "Workflow created successfully", workflow.id)
        return res

    @staticmethod
    @transaction.atomic
    def updateWorkflow(
        id: int,
        name: str,
        scheduleId: int,
        triggerWorkflowId: int,
        triggerWorkflowStatus: str,
        notebookIds: List[int],
    ):
        """
        Updates workflow
        :param name: name of new workflow
        :param scheduleId: crontab id
        :param triggerWorkflowId: id of workflow which triggers this workflow
        :param triggerWorkflowStatus: ["success", "failure", "always"] required
                status of triggerWorkflow to trigger this workflow
        :param notebookIds: notebookIds for workflow
        """
        res = ApiResponse(message="Error in updating workflow")
        workflow = Workflow.objects.filter(id=id).update(
            name=name,
            crontab_id=scheduleId,
            triggerWorkflow_id=triggerWorkflowId,
            triggerWorkflowStatus=triggerWorkflowStatus,
        )
        NotebookJob.objects.filter(workflow_id=id).delete()
        notebookJobs = [
            NotebookJob(workflow_id=id, notebookId=notebookId)
            for notebookId in notebookIds
        ]
        NotebookJob.objects.bulk_create(notebookJobs)

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

    @staticmethod
    def updateTriggerWorkflow(workflowId: int, triggerWorkflowId: int, triggerWorkflowStatus: int):
        """Update given workflow's trigger workflow"""
        res = ApiResponse(message="Error in updating trigger workflow")
        updateStatus = Workflow.objects.filter(id=workflowId).update(triggerWorkflow_id=triggerWorkflowId, triggerWorkflowStatus=triggerWorkflowStatus)
        res.update(True, "Trigger workflow updated successfully", updateStatus)
        return res

    @staticmethod
    def updateSchedule(workflowId: int, scheduleId: int):
        """Update given workflow's schedule"""
        res = ApiResponse(message="Error in updating workflow schedule")
        updateStatus = Workflow.objects.filter(id=workflowId).update(crontab_id=scheduleId)
        res.update(True, "Workflow schedule updated successfully", True)
        return res

    @staticmethod
    def runWorkflow(workflowId: int, workflowRunId: int = None):
        """
        Runs workflow
        """
        # TODO If workflow already
        notebookIds = list(
            NotebookJob.objects.filter(workflow_id=workflowId).values_list(
                "notebookId", flat=True
            )
        )
        if workflowRunId:
            workflowRun = WorkflowRun.objects.get(id=workflowRunId)
            workflowRun.status = STATUS_RUNNING
            workflowRun.save()
        else:
            workflowRun = WorkflowRun.objects.create(
                workflow_id=workflowId, status=STATUS_RUNNING
            )
        notebookRunStatusIds = []
        for notebookId in notebookIds:
            runStatus = RunStatus.objects.create(
                notebookId=notebookId, status=NOTEBOOK_STATUS_RUNNING, runType="Scheduled"
            )
            runNotebookJobTask.delay(notebookId=notebookId, runStatusId=runStatus.id)
            notebookRunStatusIds.append(runStatus.id)

        workflowStatus = polling.poll(
            lambda: WorkflowServices.__checkGivenRunStatuses(notebookRunStatusIds)
            != "stillRunning",
            step=3,
            timeout=3600,
        )

        if workflowStatus:
            workflowRun.status = STATUS_SUCCESS
            workflowRun.save()
        else:
            workflowRun.status = STATUS_FAILURE
            workflowRun.save()

        dependentWorkflowIds = list(
            Workflow.objects.filter(
                triggerWorkflow_id=workflowId,
                triggerWorkflowStatus__in=[STATUS_ALWAYS, workflowRun.status],
            ).values_list("id", flat=True)
        )
        return dependentWorkflowIds

    @staticmethod
    def __checkGivenRunStatuses(notebookRunStatusIds: List[int]):
        """Check if given runStatuses are status is SUCCESS"""

        if (
            len(notebookRunStatusIds)
            == RunStatus.objects.filter(id__in=notebookRunStatusIds)
            .exclude(status=NOTEBOOK_STATUS_RUNNING)
            .count()
        ):
            return (
                len(notebookRunStatusIds)
                == RunStatus.objects.filter(
                    id__in=notebookRunStatusIds, status=NOTEBOOK_STATUS_SUCCESS
                ).count()
            )

        return "stillRunning"


class WorkflowActions:
    @staticmethod
    def runWorkflow(workflowId: int):
        """
        Runs given workflow
        """
        from workflows.tasks import runWorkflowJob

        res = ApiResponse(message="Error in running workflow")

        existingWorkflows = WorkflowRun.objects.filter(workflow_id=workflowId).order_by(
            "-startTimestamp"
        )
        if existingWorkflows.count() and existingWorkflows[0].status in [
            STATUS_RUNNING,
            STATUS_RECEIVED,
        ]:
            res.update(False, "Can't run already running workflow")
            return res

        workflowRun = WorkflowRun.objects.create(
            workflow_id=workflowId, status=STATUS_RECEIVED
        )
        runWorkflowJob.delay(workflowId=workflowId, workflowRunId=workflowRun.id)
        res.update(True, "Ran workflow successfully")
        return res

    @staticmethod
    def stopWorkflow(workflowId: int):
        """
        Stops given workflow
        """
        res = ApiResponse(message="Error in stopping workflow")
        notebookIds = list(
            NotebookJob.objects.filter(workflow_id=workflowId).values_list(
                "notebookId", flat=True
            )
        )

        workflowRuns = WorkflowRun.objects.filter(workflow_id=workflowId).order_by("-startTimestamp")
        if workflowRuns.count():
            status = workflowRuns[0].status
            # implement celery stop
        res.update(True, "Stopped workflow successfully")
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
