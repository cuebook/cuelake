from typing import List
import os
import math
import logging
import datetime as dt
import polling
from workflows.models import (
    Workflow,
    WorkflowRun,
    NotebookJob,
    STATUS_SUCCESS,
    STATUS_ERROR,
    STATUS_ALWAYS,
    STATUS_RUNNING,
    STATUS_ABORTED
)
from utils.zeppelinAPI import Zeppelin

from genie.tasks import runNotebookJob as runNotebookJobTask
from genie.models import NOTEBOOK_STATUS_QUEUED, RunStatus, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_SUCCESS

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Name of the celery task which runs the notebook job
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"
NOTEBOOK_BATCH_COUNT = os.environ.get("NOTEBOOK_BATCH_COUNT", 10)

class TaskUtils:
    """
    Class containing workflow job utils
    """
    @staticmethod
    def runWorkflow(workflowId: int, workflowRunId: int = None):
        """
        Runs workflow
        """
        notebookIds = TaskUtils.__getNotebookIdsInWorkflow(workflowId)
        workflowRun = TaskUtils.__getOrCreateWorkflowRun(workflowId, workflowRunId)
        successFlag = True
        for index in range(int(math.ceil(len(notebookIds) / NOTEBOOK_BATCH_COUNT))):
            # processing one batch of notebooks at a time
            batchNotebookIds = notebookIds[index * NOTEBOOK_BATCH_COUNT:(index + 1) * NOTEBOOK_BATCH_COUNT]
            notebookRunStatusIds = TaskUtils.__runNotebookJobsFromList(batchNotebookIds)
            workflowStatus = polling.poll(
                lambda: TaskUtils.__checkGivenRunStatuses(notebookRunStatusIds),
                check_success= lambda x: x != "RUNNING",
                step=3,
                timeout=3600*6,
            )
            if not workflowStatus and successFlag:
                successFlag = False
            logger.info(f"Finished batch {index + 1}. Restarting spark interpreter")
            if not workflowStatus:
                logger.info(f"Error occured in this batch. Notebook Ids: {batchNotebookIds}")
            Zeppelin.restartInterpreter("spark")

        if WorkflowRun.objects.get(id=workflowRun.id).status == STATUS_ABORTED:
            return []

        workflowRun.status = STATUS_SUCCESS if successFlag else STATUS_ERROR
        workflowRun.endTimestamp = dt.datetime.now()
        workflowRun.save()

        dependentWorkflowIds = list(
            Workflow.objects.filter(
                triggerWorkflow_id=workflowId,
                triggerWorkflowStatus__in=[STATUS_ALWAYS, workflowRun.status],
            ).values_list("id", flat=True)
        )
        return dependentWorkflowIds

    @staticmethod
    def __runNotebookJobsFromList(notebookIds: List[int]):
        """
        Runs notebook jobs for all notebookIds
        """
        notebookRunStatusIds = []
        for notebookId in notebookIds:
            runStatus = RunStatus.objects.create(
                notebookId=notebookId, status=NOTEBOOK_STATUS_QUEUED, runType="Workflow"
            )
            runNotebookJobTask.delay(notebookId=notebookId, runStatusId=runStatus.id)
            notebookRunStatusIds.append(runStatus.id)
        return notebookRunStatusIds
    
    @staticmethod
    def __getNotebookIdsInWorkflow(workflowId: int):
        """
        Returns list of notebook ids in a workflow
        """
        notebookIds = list(
            NotebookJob.objects.filter(workflow_id=workflowId).values_list(
                "notebookId", flat=True
            )
        )
        return notebookIds

    @staticmethod
    def __getOrCreateWorkflowRun(workflowId: int, workflowRunId: int = None):
        """
        Gets or Creates workflow run object
        """
        if workflowRunId:
            workflowRun = WorkflowRun.objects.get(id=workflowRunId)
            workflowRun.status = STATUS_RUNNING
            workflowRun.save()
        else:
            workflowRun = WorkflowRun.objects.create(
                workflow_id=workflowId, status=STATUS_RUNNING
            )
        return workflowRun
    
    @staticmethod
    def __checkGivenRunStatuses(notebookRunStatusIds: List[int]):
        """
        Check if given runStatuses are status is SUCCESS
        """
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

        return "RUNNING"
