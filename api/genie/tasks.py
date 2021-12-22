import os
import json
import uuid
import datetime as dt
import dateutil.parser as dp
import polling
from celery import shared_task
from django.conf import settings

from genie.models import NotebookRunLogs, NOTEBOOK_STATUS_SUCCESS, NOTEBOOK_STATUS_ERROR, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_FINISHED, NOTEBOOK_STATUS_ABORT, NOTEBOOK_STATUS_QUEUED
from system.services import NotificationServices
from utils.zeppelinAPI import ZeppelinAPI
from utils.kubernetesAPI import Kubernetes
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

ZEPPELIN_API_RETRY_COUNT = 3
ZEPPELIN_SERVER_CONCURRENCY = os.environ.get("ZEPPELIN_SERVER_CONCURRENCY", 5)
ZEPPELIN_JOB_SERVER_PREFIX = "zeppelin-job-server-"

@shared_task
def runNotebookJob(notebookId: str, workspaceId: int, notebookRunLogsId: int = None, runType: str = "Scheduled"):
    """
    Celery task to run a zeppelin notebook
    :param notebookId: ID of the zeppelin notebook which to run
    :param notebookRunLogsId: ID of genie.notebookRunLogs model
    """
    notebookName = notebookId # Initialize notebook name with notebook id
    logger.info(f"Starting notebook job for: {notebookId}")
    taskId = runNotebookJob.request.id # Celery task id
    taskId = taskId if taskId else ""
    notebookRunLogs = __getOrCreateNotebookRunLogs(notebookRunLogsId, notebookId, runType, taskId, workspaceId)
    try:
        zeppelinServerId = __allocateZeppelinServer(notebookRunLogs, workspaceId)
        logger.info(f"Notebook {notebookId} scheduled to run on {zeppelinServerId}")
        zeppelin = ZeppelinAPI(zeppelinServerId)
        __waitUntilServerReady(zeppelinServerId, zeppelin)
        isRunning, notebookName = __checkIfNotebookRunning(notebookId, zeppelin) # change to get only notebook name
        # Clear notebook results
        zeppelin.clearNotebookResults(notebookId)
        response = zeppelin.runNotebookJob(notebookId)
        if response:
            try:
                polling.poll(
                    lambda: __checkIfNotebookRunningAndStoreLogs(notebookId, notebookRunLogs, zeppelin) != True, step=3, timeout=3600*6
                )
                __evaluateScaleDownZeppelin()
            except Exception as ex:
                logger.error(f"Error occured in notebook {notebookId}. Error: {str(ex)}")
                notebookRunLogs.status = NOTEBOOK_STATUS_ERROR
                notebookRunLogs.message = str(ex)
                notebookRunLogs.endTimestamp = dt.datetime.now()
                notebookRunLogs.save()
                NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=str(ex))
        else:
            logger.error(f"Error occured in notebook {notebookId}. Error: Failed to trigger notebook job")
            notebookRunLogs.status=NOTEBOOK_STATUS_ERROR
            notebookRunLogs.message = "Failed running notebook"
            notebookRunLogs.endTimestamp = dt.datetime.now()
            notebookRunLogs.save()

    except Exception as ex:
        logger.error(f"Error occured in notebook {notebookId}. Error: {str(ex)}")
        notebookRunLogs.status=NOTEBOOK_STATUS_ERROR
        notebookRunLogs.message = str(ex)
        notebookRunLogs.endTimestamp = dt.datetime.now()
        notebookRunLogs.save()
        NotificationServices.notify(notebookName=notebookName if notebookName else notebookId, isSuccess=False, message=str(ex))

def __allocateZeppelinServer(notebookRunLogs: NotebookRunLogs, workspaceId: int):
    """
    Creates or allocates a zeppelin server to run the notebook on
    """
    zeppelinServerNotebookMap = __getZeppelinServerNotebookMap()
    zeppelinServerId = __getOrCreateZeppelinServerId(zeppelinServerNotebookMap, workspaceId)
    notebookRunLogs.zeppelinServerId = zeppelinServerId
    notebookRunLogs.save()
    return zeppelinServerId

def __getZeppelinServerNotebookMap():
    notebookRuns = NotebookRunLogs.objects.filter(status__in=[NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_QUEUED])
    zeppelinServerNotebookMap = {} # this contains number of running jobs per zeppelinServerId
    for notebookRun in notebookRuns:
        if notebookRun.zeppelinServerId != "" and notebookRun.zeppelinServerId in zeppelinServerNotebookMap:
            zeppelinServerNotebookMap[notebookRun.zeppelinServerId] += 1
        elif notebookRun.zeppelinServerId != "":
            zeppelinServerNotebookMap[notebookRun.zeppelinServerId] = 1
    return zeppelinServerNotebookMap

def __getOrCreateZeppelinServerId(zeppelinServerMap, workspaceId):
    for zeppelinServerId, runningNotebooks in zeppelinServerMap.items():
        if runningNotebooks < ZEPPELIN_SERVER_CONCURRENCY:
            return zeppelinServerId
    randomId = uuid.uuid4().hex.lower()[0:20]
    zeppelinServerId = ZEPPELIN_JOB_SERVER_PREFIX + randomId
    Kubernetes.addZeppelinJobServer(zeppelinServerId, workspaceId)
    return zeppelinServerId

def __waitUntilServerReady(zeppelinServerId: str, zeppelin: ZeppelinAPI):
    polling.poll(
        lambda: Kubernetes.getPodStatus(zeppelinServerId) == 'Running', step=3, timeout=3600*6
    )
    if os.environ.get("ENVIRONMENT","") == "dev": 
        # To port forward zeppelin job server for local devlopment
        port =  Kubernetes.portForward(zeppelinServerId)
        zeppelin.setZeppelinAddress("localhost", port)
        
    polling.poll(
        lambda: zeppelin.healthCheck() != False, step=3, timeout=3600*6
    )

def __getOrCreateNotebookRunLogs(notebookRunLogsId: int, notebookId: str, runType: str, taskId: str, workspaceId: int):
    """
    Gets or creates a notebook run status object
    """
    if not notebookRunLogsId:
        notebookRunLog = NotebookRunLogs.objects.create(notebookId=notebookId, status=NOTEBOOK_STATUS_RUNNING, runType=runType, taskId=taskId, workspace_id=workspaceId)
    else:
        notebookRunLog = NotebookRunLogs.objects.get(id=notebookRunLogsId)
        notebookRunLog.startTimestamp = dt.datetime.now()
        notebookRunLog.status = NOTEBOOK_STATUS_RUNNING
        notebookRunLog.taskId = taskId
        notebookRunLog.save()
    return notebookRunLog

def __checkIfNotebookRunning(notebookId: str, zeppelin: ZeppelinAPI):
    """
    Checks if notebook is running and returns tuple of isNotebookRunning, notebookName
    """
    response = zeppelin.getNotebookDetails(notebookId)
    isNotebookRunning = False
    notebookName = ""
    if response:
        isNotebookRunning = response.get("info", {}).get("isRunning", False)
        notebookName = response.get("name", "")
    return isNotebookRunning, notebookName

def __checkIfNotebookRunningAndStoreLogs(notebookId: str, notebookRunLogs: NotebookRunLogs, zeppelin: ZeppelinAPI):
    """
    Checks if notebook is running and stores logs
    """
    response = zeppelin.getNotebookDetailsWithRetry(notebookId)
    logger.info(response)
    if response:
        notebookRunLogs.logs = json.dumps(response)
        notebookRunLogs.save()
        isNotebookRunning = response.get("info", {}).get("isRunning", False)
        if not isNotebookRunning:
            if(__checkIfRetryable(response)):
                __rerunNotebook(notebookId, zeppelin)
                return True
            __setNotebookStatus(response, notebookRunLogs)
        return isNotebookRunning
    else:
        __setNotebookStatus(response, notebookRunLogs)
        return False

def __rerunNotebook(notebookId: str, zeppelin: ZeppelinAPI):
    zeppelin.runNotebookJob(notebookId)

def __checkIfRetryable(response):
    responseString = json.dumps(response)
    if "org.apache.zeppelin.interpreter.InterpreterException: java.lang.NullPointerException" in responseString:
        logger.error(f"Error occured in opening a new interpreter instance. Retrying.")
        logger.error(f"{responseString}")
        return True
    elif "org.apache.zeppelin.spark.SparkSqlInterpreter.internalInterpret(SparkSqlInterpreter.java:80)" in responseString:
        logger.error(f"Error occured in opening a new interpreter instance. Retrying.")
        logger.error(f"{responseString}")
        return True
    else:
        return False

def __setNotebookStatus(response, notebookRunLogs: NotebookRunLogs):
    """
    Sets notebook run status based on the response
    """
    if response:
        paragraphs = response.get("paragraphs", [])
        notebookName = response.get("name", "")
        for paragraph in paragraphs:
            if paragraph.get("status") != "FINISHED":
                notebookRunLogs.status=NOTEBOOK_STATUS_ABORT if paragraph.get("status") == "ABORT" else NOTEBOOK_STATUS_ERROR
                notebookRunLogs.endTimestamp = dt.datetime.now()
                notebookRunLogs.save()
                NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=paragraph.get("title", "") + " " + paragraph.get("id","") + " failed")
                return
    notebookRunLogs.status=NOTEBOOK_STATUS_SUCCESS if response else NOTEBOOK_STATUS_ERROR 
    notebookRunLogs.endTimestamp = dt.datetime.now()
    notebookRunLogs.save()
    NotificationServices.notify(notebookName=notebookName, isSuccess=True, message="Run successful")

def __evaluateScaleDownZeppelin():
    pods = Kubernetes.getPods()
    zeppelinServerPods = []
    for pod in pods:
        if ZEPPELIN_JOB_SERVER_PREFIX in pod.metadata.name:
            zeppelinServerPods.append(pod)
    zeppelinServerNotebookMap = __getZeppelinServerNotebookMap()
    for pod in zeppelinServerPods:
        if pod.metadata.name not in zeppelinServerNotebookMap:
            logger.info(f"Removing zeppelin server: {pod.metadata.name}")
            Kubernetes.removeZeppelinServer(pod.metadata.name)
