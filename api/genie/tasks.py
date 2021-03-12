import os
import requests
from celery import shared_task

ZEPPELIN_HOST = os.environ.get("ZEPPELIN_HOST")
ZEPPELIN_PORT = os.environ.get("ZEPPELIN_PORT")

@shared_task
def runNotebookJob(notebookId: str):
    """
    Celery task to run a zeppelin notebook
    :param notebookId: ID of the zeppelin notebook which to run
    """
    zeppelinUrl = f"http://{ZEPPELIN_PORT}:{ZEPPELIN_PORT}/api/notebook/job/{notebookId}"
    requests.post(zeppelinUrl)
