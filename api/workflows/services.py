from typing import List
import asyncio
import json
import pytz
import time
import datetime as dt
from django.db import transaction
import polling
from workflows.models import (
    Workflow,
    WorkflowRun,
    NotebookJob,
    STATUS_SUCCESS,
    STATUS_ERROR,
    STATUS_ALWAYS,
    STATUS_RUNNING,
    STATUS_RECEIVED,
    STATUS_ABORTED
)
from workflows.serializers import WorkflowSerializer, WorkflowRunSerializer
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import Zeppelin

from genie.tasks import runNotebookJob as runNotebookJobTask
from genie.services import NotebookJobServices
from genie.models import RunStatus, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_SUCCESS

from django_celery_beat.models import CrontabSchedule
# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"


class WorkflowServices:
    """
    Class containing services related to NotebookJob model
    """

    @staticmethod
    def getWorkflows(offset: int = 0, sortOn : str = None, isAsc : str = None):
        """
        Service to fetch and serialize Workflows
        :param offset: Offset for fetching NotebookJob objects
        """
        LIMIT = 25
        res = ApiResponse(message="Error retrieving workflows")
        workflows = Workflow.objects.filter(enabled=True).order_by("-id")
        if(sortOn):
            workflows = WorkflowServices.sortingOnWorkflows(workflows, sortOn, isAsc)
        total = workflows.count()
        data = WorkflowSerializer(workflows[offset:offset+LIMIT], many=True).data

        res.update(
            True,
            "Workflows retrieved successfully",
            {"total": total, "workflows": data},
        )
        return res

    @staticmethod
    def sortingOnWorkflows(workflows, sortOn, isAsc):
        if sortOn == 'name' and isAsc == "ascend":
            workflows = Workflow.objects.filter(enabled=True).order_by("name")

        if sortOn == 'name' and isAsc == "descend":
            workflows = Workflow.objects.filter(enabled=True).order_by("-name")

        if sortOn == 'triggerWorkflow' and isAsc == "ascend":
            workflows = Workflow.objects.filter(enabled=True).order_by("triggerWorkflow__name")

        if sortOn == 'triggerWorkflow' and isAsc == "descend":
            workflows = Workflow.objects.filter(enabled=True).order_by("-triggerWorkflow__name")

        if sortOn == "schedule" and isAsc == "ascend":
            workflows = Workflow.objects.filter(enabled=True).order_by("crontab__customschedule__name")

        if sortOn == "schedule" and isAsc == "descend":
            workflows = Workflow.objects.filter(enabled=True).order_by("-crontab__customschedule__name")

        if sortOn == "lastRunTime" and isAsc == "ascend":
            workflows = Workflow.objects.filter(enabled=True).order_by("last_run_at")
        if sortOn == "lastRunTime" and isAsc == "descend":
            workflows = Workflow.objects.filter(enabled=True).order_by("-last_run_at")

        # if sortOn == "lastRunStatus" and isAsc == "ascend":
        #     workflows = Workflow.objects.filter(enabled=True).order_by("workflowrun__status")

        # if sortOn == "lastRunStatus" and isAsc == "descend":
        #     workflows = Workflow.objects.filter(enabled=True).order_by("workflowrun__status")

        return workflows



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
        # cronTab Id 1 is schedule that never runs

        workflow = Workflow.objects.create(
            name=name,
            crontab_id=scheduleId if scheduleId else 1,
            triggerWorkflow_id=triggerWorkflowId,
            triggerWorkflowStatus=triggerWorkflowStatus,
            task="workflows.tasks.runWorkflowJob"
        )
        workflow.args = str([workflow.id])
        workflow.save()
        
        notebookJobs = [
            NotebookJob(workflow_id=workflow.id, notebookId=notebookId)
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
            crontab_id=scheduleId if scheduleId else 1,
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
    def deleteWorkflow(workflowId: int):
        """
        Delete workflow
        :param workflowId: id of Workflows.Workflow
        """
        res = ApiResponse(message="Error in deleting workflow logs")
        count = Workflow.objects.filter(id=workflowId).delete()
        res.update(True, "Workflow deleted successfully")
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
        data = WorkflowRunSerializer(workflowRuns[offset:offset+LIMIT], many=True).data

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
        updateStatus = Workflow.objects.filter(id=workflowId).update(crontab_id=scheduleId if scheduleId else 1)
        res.update(True, "Workflow schedule updated successfully", True)
        return res


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
            workflowRun = workflowRuns[0]
            workflowRun.status = STATUS_ABORTED
            workflowRun.endTimestamp = dt.datetime.now()
            workflowRun.save()

        notebookIds = Workflow.objects.get(id=workflowId).notebookjob_set.all().values_list("notebookId", flat=True)
        responses = [ NotebookJobServices.stopNotebookJob(notebookId) for notebookId in notebookIds ]

        res.update(True, "Stopped workflow successfully")
        return res
