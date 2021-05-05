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


@shared_task
def runNotebookJob(notebookId: str, runStatusId: int = None, runType: str = "Scheduled"):
    """
    Celery task to run a zeppelin notebook
    :param notebookId: ID of the zeppelin notebook which to run
    :param runStatusId: ID of genie.runStatus model
    """
    if not runStatusId:
        runStatus = RunStatus.objects.create(notebookId=notebookId, status=NOTEBOOK_STATUS_RUNNING, runType=runType)
    else:
        runStatus = RunStatus.objects.get(id=runStatusId)
        runStatus.startTimestamp = dt.datetime.now()
        runStatus.save()

    try:
        # Check if notebook is already running
        isRunning, notebookName = checkIfNotebookRunning(notebookId)
        if(isRunning):
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
                        lambda: checkIfNotebookRunningAndStoreLogs(notebookId, runStatus) != True, step=3, timeout=3600
                    )
                except Exception as ex:
                    runStatus.status = NOTEBOOK_STATUS_ERROR
                    runStatus.message = str(ex)
                    runStatus.save()
                    NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=str(ex))
            else:
                runStatus.status=NOTEBOOK_STATUS_ERROR
                runStatus.message = "Failed running notebook"
                runStatus.save()
    except Exception as ex:
        runStatus.status=NOTEBOOK_STATUS_ERROR
        runStatus.message = str(ex)
        runStatus.save()
        NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=str(ex))

def checkIfNotebookRunning(notebookId: str):
    response = Zeppelin.getNotebookDetails(notebookId)
    isNotebookRunning = response.get("info", {}).get("isRunning", False)
    notebookName = response.get("name", "Undefined")
    return isNotebookRunning, notebookName

def checkIfNotebookRunningAndStoreLogs(notebookId, runStatus):
    response = Zeppelin.getNotebookDetails(notebookId)
    runStatus.logs = json.dumps(response)
    runStatus.save()
    isNotebookRunning = response.get("info", {}).get("isRunning", False)
    if not isNotebookRunning:
        setNotebookStatus(response, runStatus)
    return isNotebookRunning

def setNotebookStatus(response: dict, runStatus: RunStatus):
    paragraphs = response.get("paragraphs", [])
    notebookName = response.get("name", "Undefined")
    for paragraph in paragraphs:
        if paragraph.get("status") != "FINISHED":
            runStatus.status=NOTEBOOK_STATUS_ERROR
            runStatus.save()
            NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=paragraph.get("title") + " " + paragraph.get("id") + " failed")
            return
    runStatus.status=NOTEBOOK_STATUS_SUCCESS
    runStatus.save()
    NotificationServices.notify(notebookName=notebookName, isSuccess=True, message="Run successful")