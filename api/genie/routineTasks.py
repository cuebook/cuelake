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
    from genie.models import RunStatus, NOTEBOOK_STATUS_RUNNING
    runStatuses = RunStatus.objects.filter(status__in=[NOTEBOOK_STATUS_RUNNING])
    if len(runStatuses):
        staleRunStatues = []
        for runStatus in runStatuses:
            if((datetime.now(timezone.utc) - runStatus.updateTimestamp).seconds > 30):
                staleRunStatues.append(runStatus)
                __handleStaleNotebookJob(runStatus)

def __handleStaleNotebookJob(runStatus):
    # First check if job server is running:
    from utils.kubernetesAPI import Kubernetes
    from genie.tasks import runNotebookJob
    podStatus = None
    try:
        podStatus = Kubernetes.getPodStatus(runStatus.zeppelinServerId)
        if podStatus in ["RUNNING", "PENDING"]:
            return True
    except Exception as ex:
        # This will be mostly pod not found error
        logger.info(f"{str(ex)}")
    # Run the job again
    runNotebookJob.delay(notebookId=runStatus.notebookId, runStatusId=runStatus.id)

def __checkOrphanWorkflowJobs():
    from workflows.models import WorkflowRun, STATUS_RUNNING
    workflowRuns = WorkflowRun.objects.filter(status=STATUS_RUNNING)
    if len(workflowRuns):
        for workflowRun in workflowRuns:
            ___checkAndUpdateWorkflowStatus(workflowRun)

def ___checkAndUpdateWorkflowStatus(workflowRun):
    from workflows.models import STATUS_RUNNING, STATUS_QUEUED, STATUS_ABORTED, STATUS_ERROR, STATUS_SUCCESS
    if workflowRun.runstatus_set.filter(status__in=[STATUS_RUNNING,STATUS_QUEUED]).count() == 0:
        workflowRun.endTimestamp = datetime.now()
        if workflowRun.runstatus_set.filter(status__in=[STATUS_ERROR, STATUS_ABORTED]).count() == 0:
            workflowRun.status = STATUS_SUCCESS
            workflowRun.save()
        else:
            workflowRun.status = STATUS_ERROR
            workflowRun.save()
                