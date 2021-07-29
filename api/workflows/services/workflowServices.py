from typing import List
from django.db import transaction

from app.celery import app

from workflows.models import (
    Workflow,
    WorkflowRunLogs,
    WorkflowNotebookMap
)
from workflows.serializers import WorkflowSerializer, WorkflowRunLogsSerializer
from utils.apiResponse import ApiResponse
from django_celery_beat.models import PeriodicTask

class WorkflowServices:
    """
    Class containing services related to NotebookJob model
    """

    @staticmethod
    def getWorkflows(offset: int = 0, limit: int = 25, sortColumn : str = None, sortOrder : str = None):
        """
        Service to fetch and serialize Workflows
        :param offset: Offset for fetching NotebookJob objects
        """
        res = ApiResponse(message="Error retrieving workflows")
        workflows = Workflow.objects.order_by("-id")
        total = workflows.count()

        if(sortColumn):
            isAscending = True if sortOrder == "ascend" else False
            workflows = WorkflowServices.sortingOnWorkflows(workflows, sortColumn, isAscending)
        data = WorkflowSerializer(workflows[offset : offset+limit], many=True).data

        res.update(
            True,
            "Workflows retrieved successfully",
            {"total": total, "workflows": data},
        )
        return res

    @staticmethod
    def sortingOnWorkflows(workflows: List[Workflow], sortColumn: str, isAscending: bool):
        sortPrefix = "" if isAscending else "-"
        if sortColumn == 'name':
            workflows = Workflow.objects.all().order_by(sortPrefix + "name")
        if sortColumn == 'triggerWorkflow':
            workflows = Workflow.objects.all().order_by(sortPrefix + "triggerWorkflow__name")
        if sortColumn == "schedule":
            workflows = Workflow.objects.all().order_by(sortPrefix + "periodictask__crontab__customschedule__name")
        if sortColumn == "lastRunTime":
            workflowRuns = WorkflowRunLogs.objects.all().order_by("workflow_id", "-startTimestamp").distinct("workflow_id").values("workflow_id", "startTimestamp")
            sortedWorkflowRuns = sorted(workflowRuns, key = lambda i: i['startTimestamp'], reverse=isAscending)
            sortedWorkflowIds = [workflowRun["workflow_id"] for workflowRun in sortedWorkflowRuns]
            workflows = Workflow.objects.filter(id__in=sortedWorkflowIds)
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
        periodictask = None
        workflow = Workflow.objects.create(
            name=name,
            periodictask=periodictask,
            triggerWorkflow_id=triggerWorkflowId,
            triggerWorkflowStatus=triggerWorkflowStatus
        )
        if scheduleId:
            periodictask = PeriodicTask.objects.create(
                crontab_id=scheduleId,
                name=name,
                task="workflows.tasks.runWorkflowJob",
                args = str([workflow.id])
            )
            workflow.periodictask = periodictask
            workflow.save()
        
        notebookJobs = [
            WorkflowNotebookMap(workflow_id=workflow.id, notebookId=notebookId)
            for notebookId in notebookIds
        ]
        WorkflowNotebookMap.objects.bulk_create(notebookJobs)
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
        workflow = Workflow.objects.get(id=id)
        if not workflow:
            return res

        workflow.name = name
        workflow.triggerWorkflow_id = triggerWorkflowId
        workflow.triggerWorkflowStatus = triggerWorkflowStatus
        workflow.save()
        if scheduleId:
            if workflow.periodictask:
                workflow.periodictask.crontab_id = scheduleId
                workflow.periodictask.save()
            else:
                periodictask = PeriodicTask.objects.create(
                    crontab_id=scheduleId,
                    name=name,
                    task="workflows.tasks.runWorkflowJob",
                    args = str([workflow.id])
                )
                workflow.periodictask = periodictask
                workflow.save()
        else:
            if workflow.periodictask:
                PeriodicTask.objects.get(id=workflow.periodictask).delete()
                workflow.periodictask = None
                workflow.save()
            
        WorkflowNotebookMap.objects.filter(workflow_id=id).delete()
        notebookJobs = [
            WorkflowNotebookMap(workflow_id=id, notebookId=notebookId)
            for notebookId in notebookIds
        ]
        WorkflowNotebookMap.objects.bulk_create(notebookJobs)
        res.update(True, "Workflow updated successfully", None)
        return res

    @staticmethod
    def deleteWorkflow(workflowId: int):
        """
        Delete workflow
        :param workflowId: id of Workflows.Workflow
        """
        res = ApiResponse(message="Error in deleting workflow logs")
        Workflow.objects.filter(id=workflowId).delete()
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
        workflowRuns = WorkflowRunLogs.objects.filter(workflow=workflowId).order_by("-id")
        total = workflowRuns.count()
        data = WorkflowRunLogsSerializer(workflowRuns[offset:offset+LIMIT], many=True).data

        res.update(
            True,
            "WorkflowRuns retrieved successfully",
            {"total": total, "workflowRuns": data},
        )
        return res

    @staticmethod
    def getWorkflowRunLogs(workflowRunLogsId: int):
        """
        Service to fetch logs related to given workflowRun
        :param workflowRunLogsId: if of model workflows.workflowRun
        """
        res = ApiResponse(message="Error in retrieving workflow logs")
        workflowRun = WorkflowRunLogs.objects.get(id=workflowRunLogsId)
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
        workflow = Workflow.objects.filter(id=workflowId).first()
        if scheduleId and workflow.periodictask is not None:
            workflow.periodictask.crontab_id=scheduleId
            workflow.periodictask.save()
        elif scheduleId and workflow.periodictask is None:
            periodictask = PeriodicTask.objects.create(
                crontab_id=scheduleId,
                name=workflow.name,
                task="workflows.tasks.runWorkflowJob",
                args = str([workflow.id])
            )
            workflow.periodictask = periodictask
            workflow.save()
        else:
            PeriodicTask.objects.get(id=workflow.periodictask.id).delete()
            workflow.periodictask = None
            workflow.save()
        res.update(True, "Workflow schedule updated successfully", True)
        return res
