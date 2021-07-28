import datetime as dt
from app.celery import app
from workflows.models import (
    WorkflowRun,
    STATUS_RUNNING,
    STATUS_QUEUED,
    STATUS_ABORTED
)
from utils.apiResponse import ApiResponse

from genie.tasks import runNotebookJob as runNotebookJobTask
from genie.services import NotebookJobServices
from genie.models import CustomSchedule, NotebookRunLogs, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_SUCCESS, NOTEBOOK_STATUS_QUEUED, NOTEBOOK_STATUS_ABORT


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
            STATUS_QUEUED,
        ]:
            res.update(False, "Can't run already running workflow")
            return res

        workflowRun = WorkflowRun.objects.create(
            workflow_id=workflowId, status=STATUS_QUEUED
        )
        runWorkflowJob.delay(workflowId=workflowId, workflowRunId=workflowRun.id)
        res.update(True, "Ran workflow successfully")
        return res

    @staticmethod
    def stopWorkflow(workflowRunId: int):
        """
        Stops given workflow
        """
        res = ApiResponse(message="Error in stopping workflow")
        
        # Stopping workflow task
        workflowRun = WorkflowRun.objects.get(id=workflowRunId)
        # Revoke celery task
        app.control.revoke(workflowRun.taskId, terminate=True)
        # Update workflow run status
        workflowRun.status = STATUS_ABORTED
        workflowRun.endTimestamp = dt.datetime.now()
        workflowRun.save()

        # Stopping notebook tasks
        notebookRunLogs = NotebookRunLogs.objects.filter(workflowRun=workflowRunId)
        for notebookRunLog in notebookRunLogs:
            if notebookRunLog.status == NOTEBOOK_STATUS_QUEUED:
                app.control.revoke(notebookRunLog.taskId, terminate=True)
                notebookRunLog.status = NOTEBOOK_STATUS_ABORT
                notebookRunLog.save()
            elif notebookRunLog.status == NOTEBOOK_STATUS_RUNNING:
                notebookRunLog.status = NOTEBOOK_STATUS_ABORT
                notebookRunLog.save()
                NotebookJobServices.stopNotebookJob(notebookRunLog.notebookId)

        res.update(True, "Stopped workflow successfully")
        return res
