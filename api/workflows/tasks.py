import json
import datetime as dt
import dateutil.parser as dp
import requests
import polling
from celery import shared_task
from django.conf import settings

from system.services import NotificationServices
from workflows.services import WorkflowServices

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def runWorkflowJob(workflowId: int):
	"""
    Celery task to run a Workflow
    :param workflowId: ID of Workflows.workflow model
	"""
	dependentWorkflowIds = WorkflowServices.runWorkflow(workflowId=workflowId)
	for workflowId in dependentWorkflowIds:
		runWorkflowJob.delay(workflowId)
