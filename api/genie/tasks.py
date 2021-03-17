import os
import requests
from celery import shared_task
from django.conf import settings

@shared_task
def runNotebookJob(notebookId: str):
    """
    Celery task to run a zeppelin notebook
    :param notebookId: ID of the zeppelin notebook which to run
    """
    zeppelinUrl = f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/api/notebook/job/{notebookId}"
    requests.post(zeppelinUrl)
