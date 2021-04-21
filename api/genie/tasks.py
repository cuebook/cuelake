import json
import datetime as dt
import dateutil.parser as dp
import requests
import polling
from celery import shared_task
from django.conf import settings

from genie.models import NotebookJob, RunStatus
from system.services import NotificationServices
from utils.zeppelinAPI import Zeppelin
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


@shared_task
def runNotebookJob(notebookId: str, runType: str = "Scheduled"):
    """
    Celery task to run a zeppelin notebook
    :param notebookId: ID of the zeppelin notebook which to run
    """
    runStatus = RunStatus.objects.create(notebookId=notebookId, status="RUNNING", runType=runType)
    try:
        # Check if notebook is already running
        isRunning, notebookName = checkIfNotebookRunning(notebookId)
        if(isRunning):
            runStatus.status="ERROR"
            runStatus.message="Notebook already running"
            runStatus.save()
        else:
            # Clear noteook results
            Zeppelin.clearNotebookResults(notebookId)
            response = Zeppelin.runNotebookJob(notebookId)
            if response:
                try:
                    polling.poll(
                        lambda: checkIfNotebookRunningAndStoreLogs(notebookId, runStatus) != True, step=3, timeout=3600
                    )
                except Exception as ex:
                    runStatus.status = "ERROR"
                    runStatus.message = str(ex)
                    runStatus.save()
                    NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=str(ex))
            else:
                runStatus.status="ERROR"
                runStatus.message = "Failed running notebook"
                runStatus.save()
    except Exception as ex:
        runStatus.status="ERROR"
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
            runStatus.status="ERROR"
            runStatus.save()
            NotificationServices.notify(notebookName=notebookName, isSuccess=False, message=paragraph.get("title") + " " + paragraph.get("id") + " failed")
            return
    runStatus.status="SUCCESS"
    runStatus.save()
    NotificationServices.notify(notebookName=notebookName, isSuccess=True, message="Run successful")