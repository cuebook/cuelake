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

def _getNotebookStatus(notebookId: str, startISO: str):
    """
    Internal method to check whether a specific notebook is running or not
    Returns a string, one out of "SUCCESS", "FAILURE", "RUNNING"
    :param notebookId: ID of the zeppelin notebook which to run
    :param startISO: ISO format string of notebook run starting time to ignore old runs 
    """
    zeppelinUrl = f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/api/notebook/job/{notebookId}"
    response = requests.get(zeppelinUrl)
    if response.status_code == 200:
        responseJSON = response.json()
        if responseJSON["status"] == "OK":
            paragraphs = responseJSON["body"].get("paragraphs")
            if paragraphs:
                for para in paragraphs:
                    para["started"] = dp.parse(para["started"]).isoformat()
                if any([para["status"] == "ERROR" and para["started"][:19] > startISO[:19]  for para in paragraphs]):
                    return "FAILURE"
                if all([para["status"] == "FINISHED" and para["started"][:19] > startISO[:19] for para in paragraphs]):
                    return "SUCCESS"
    return "RUNNING"



@shared_task
def runNotebookJob(notebookId: str):
    """
    Celery task to run a zeppelin notebook
    :param notebookId: ID of the zeppelin notebook which to run
    """
    notebookJob = NotebookJob.objects.get(notebookId=notebookId)
    runStatus = RunStatus.objects.create(notebookJob=notebookJob, status="RUNNING")
    try:
        # Check if notebook is already running
        if(checkIfNotebookRunning(notebookId)):
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
                    runStatus.status = "FAILURE"
                    runStatus.message = str(ex)
                    runStatus.save()
                finally:
                    NotificationServices.notifyOnSlack(message="")
            else:
                runStatus.status="ERROR"
                runStatus.message = "Failed running notebook"
                runStatus.save()
    except Exception as ex:
        runStatus.status="ERROR"
        runStatus.message = str(ex)
        runStatus.save()

def checkIfNotebookRunning(notebookId: str):
    response = Zeppelin.getNotebookDetails(notebookId)
    isNotebookRunning = response.get("info", {}).get("isRunning", False)
    return isNotebookRunning

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
    for paragraph in paragraphs:
        if paragraph.get("status") != "FINISHED":
            runStatus.status="ERROR"
            runStatus.save()
            return
    runStatus.status="SUCCESS"
    runStatus.save()