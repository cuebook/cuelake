from celery import shared_task
import logging
from datetime import datetime, timezone

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def orphanJobsChecker():
    __checkOrphanNotebookJobs()
    __checkOrphanWorkflowJobs()
    
def __checkOrphanNotebookJobs():
    from genie.models import NotebookRunLogs, NOTEBOOK_STATUS_RUNNING
    notebookRunLogs = NotebookRunLogs.objects.filter(status__in=[NOTEBOOK_STATUS_RUNNING])
    if len(notebookRunLogs):
        staleRunStatues = []
        for notebookRunLog in notebookRunLogs:
            if((datetime.now(timezone.utc) - notebookRunLog.updateTimestamp).seconds > 60):
                staleRunStatues.append(notebookRunLog)
                __handleStaleNotebookJob(notebookRunLog)

def __handleStaleNotebookJob(notebookRunLog):
    # First check if job server is running:
    from utils.kubernetesAPI import Kubernetes
    from genie.tasks import runNotebookJob
    podStatus = None
    try:
        podStatus = Kubernetes.getPodStatus(notebookRunLog.zeppelinServerId)
        if podStatus in ["PENDING"]:
            return True
    except Exception as ex:
        # This will be mostly pod not found error
        logger.info(f"{str(ex)}")
    # Run the job again
    runNotebookJob.delay(notebookId=notebookRunLog.notebookId, notebookRunLogsId=notebookRunLog.id)

def __checkOrphanWorkflowJobs():
    from workflows.models import WorkflowRunLogs, STATUS_RUNNING
    workflowRunLogs = WorkflowRunLogs.objects.filter(status=STATUS_RUNNING)
    if len(workflowRunLogs):
        for workflowRunLog in workflowRunLogs:
            ___checkAndUpdateWorkflowStatus(workflowRunLog)

def ___checkAndUpdateWorkflowStatus(workflowRunLog):
    from workflows.models import STATUS_RUNNING, STATUS_QUEUED, STATUS_ABORTED, STATUS_ERROR, STATUS_SUCCESS
    if workflowRunLog.notebookrunlogs_set.filter(status__in=[STATUS_RUNNING,STATUS_QUEUED]).count() == 0:
        workflowRunLog.endTimestamp = datetime.now()
        if workflowRunLog.notebookrunlogs_set.filter(status__in=[STATUS_ERROR, STATUS_ABORTED]).count() == 0:
            workflowRunLog.status = STATUS_SUCCESS
            workflowRunLog.save()
        else:
            workflowRunLog.status = STATUS_ERROR
            workflowRunLog.save()
                