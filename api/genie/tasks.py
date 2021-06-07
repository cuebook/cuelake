import json
import datetime as dt
import dateutil.parser as dp
import requests
import polling
from celery import shared_task
from django.conf import settings

from genie.models import NotebookJob, RunStatus, NOTEBOOK_STATUS_SUCCESS, NOTEBOOK_STATUS_ERROR, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_FINISHED, NOTEBOOK_STATUS_ABORT
from system.services import NotificationServices
from utils.zeppelinAPI import Zeppelin
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

ZEPPELIN_API_RETRY_COUNT = 3

@shared_task
def runNotebookJob(notebookId: str, runStatusId: int = None, runType: str = "Scheduled"):
    """
    Celery task to run a zeppelin notebook
    :param notebookId: ID of the zeppelin notebook which to run
    :param runStatusId: ID of genie.runStatus model
    """
    logger.info(f"Starting notebook job for: {notebookId}")
    taskId = runNotebookJob.request.id # Celery task id
    taskId = taskId if taskId else ""
    runStatus = __getOrCreateRunStatus(runStatusId, notebookId, runType, taskId)
    try:
        # Check if notebook is already running
        isRunning, notebookName = __checkIfNotebookRunning(notebookId)
        if isRunning:
            runStatus.status=NOTEBOOK_STATUS_ERROR
            runStatus.message="Notebook already running"
            runStatus.save()
        else:
            # Clear notebook results
            Zeppelin.clearNotebookResults(notebookId)
            response = Zeppelin.runNotebookJob(notebookId)
            if response:
                try:
                    polling.poll(
                        lambda: __checkIfNotebookRunningAndStoreLogs(notebookId, runStatus) != True, step=3, timeout=3600*6
                    )
                except Exception as ex:
                    logger.error(f"Error occured in notebook {notebookId}. Error: {str(ex)}")
                    runStatus.status = NOTEBOOK_STATUS_ERROR
                    runStatus.message = str(ex)
                    runStatus.endTimestamp = dt.datetime.now()
                    runStatus.save()
                    NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=str(ex))
            else:
                logger.error(f"Error occured in notebook {notebookId}. Error: Failed to trigger notebook job")
                runStatus.status=NOTEBOOK_STATUS_ERROR
                runStatus.message = "Failed running notebook"
                runStatus.endTimestamp = dt.datetime.now()
                runStatus.save()
    except Exception as ex:
        logger.error(f"Error occured in notebook {notebookId}. Error: {str(ex)}")
        runStatus.status=NOTEBOOK_STATUS_ERROR
        runStatus.message = str(ex)
        runStatus.endTimestamp = dt.datetime.now()
        runStatus.save()
        NotificationServices.notify(notebookName=notebookName if notebookName else notebookId, isSuccess=False, message=str(ex))

def __getOrCreateRunStatus(runStatusId: int, notebookId: str, runType: str, taskId: str):
    """
    Gets or creates a notebook run status object
    """
    if not runStatusId:
        runStatus = RunStatus.objects.create(notebookId=notebookId, status=NOTEBOOK_STATUS_RUNNING, runType=runType, taskId=taskId)
    else:
        runStatus = RunStatus.objects.get(id=runStatusId)
        runStatus.startTimestamp = dt.datetime.now()
        runStatus.status = NOTEBOOK_STATUS_RUNNING
        runStatus.taskId = taskId
        runStatus.save()
    return runStatus

def __checkIfNotebookRunning(notebookId: str):
    """
    Checks if notebook is running and returns tuple of isNotebookRunning, notebookName
    """
    response = Zeppelin.getNotebookDetails(notebookId)
    isNotebookRunning = False
    notebookName = ""
    if response:
        isNotebookRunning = response.get("info", {}).get("isRunning", False)
        notebookName = response.get("name", "")
    return isNotebookRunning, notebookName

def __checkIfNotebookRunningAndStoreLogs(notebookId, runStatus):
    """
    Checks if notebook is running and stores logs
    """
    response = Zeppelin.getNotebookDetailsWithRetry(notebookId)
    if response:
        runStatus.logs = json.dumps(response)
        runStatus.save()
        isNotebookRunning = response.get("info", {}).get("isRunning", False)
        if not isNotebookRunning:
            if(__checkIfRetryable(response)):
                __rerunNotebook(notebookId)
                return True
            __setNotebookStatus(response, runStatus)
        return isNotebookRunning
    else:
        __setNotebookStatus(response, runStatus)
        return False

def __rerunNotebook(notebookId):
    Zeppelin.runNotebookJob(notebookId)

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

def __setNotebookStatus(response, runStatus: RunStatus):
    """
    Sets notebook run status based on the response
    """
    if response:
        paragraphs = response.get("paragraphs", [])
        notebookName = response.get("name", "")
        for paragraph in paragraphs:
            if paragraph.get("status") != "FINISHED":
                runStatus.status=NOTEBOOK_STATUS_ABORT if paragraph.get("status") == "ABORT" else NOTEBOOK_STATUS_ERROR
                runStatus.endTimestamp = dt.datetime.now()
                runStatus.save()
                NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=paragraph.get("title", "") + " " + paragraph.get("id","") + " failed")
                return
    runStatus.status=NOTEBOOK_STATUS_SUCCESS if response else NOTEBOOK_STATUS_ERROR 
    runStatus.endTimestamp = dt.datetime.now()
    runStatus.save()
    NotificationServices.notify(notebookName=notebookName, isSuccess=True, message="Run successful")