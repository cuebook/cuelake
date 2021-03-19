import json
import datetime as dt
import dateutil.parser as dp
import requests
import polling
from celery import shared_task
from django.conf import settings

from genie.models import NotebookJob, RunStatus

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
    zeppelinUrl = f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/api/notebook/job/{notebookId}"
    notebookJob = NotebookJob.objects.get(notebookId=notebookId)
    startISO = dt.datetime.now(dt.timezone.utc).isoformat()
    response = requests.post(zeppelinUrl)
    if response.status_code == 200 and response.json()["status"] == "OK":
        runStatus = RunStatus.objects.create(notebookJob=notebookJob, status="RUNNING")
        finalStatus = ""
        try:
            polling.poll(
                lambda: _getNotebookStatus(notebookId, startISO) != "RUNNING", step=5, timeout=3600,
            )
        except Exception as ex:
            finalStatus = "FAILURE"
        else:
            finalStatus = _getNotebookStatus(notebookId, startISO)
        finally:
            runStatus.status = finalStatus
            logResponse = requests.get(zeppelinUrl)
            if logResponse.status_code == 200:
                logResponseJSON = logResponse.json()
                if logResponseJSON["status"] == "OK":
                    runStatus.logs = json.dumps(logResponseJSON["body"])
            runStatus.save()
