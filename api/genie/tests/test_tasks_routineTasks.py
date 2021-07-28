import pytest
import datetime as dt
from unittest import mock
from django.urls import reverse
from genie.models import NotebookRunLogs, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_SUCCESS, NOTEBOOK_STATUS_ERROR
from workflows.models import WorkflowRun, STATUS_RUNNING, STATUS_SUCCESS, STATUS_ERROR
from mixer.backend.django import mixer
from conftest import populate_seed_data
from genie.routineTasks import orphanJobsChecker


@pytest.mark.django_db
def test_getMetastoreTables(client, populate_seed_data, mocker):
    notebookRunLogs = mixer.blend("genie.notebookRunLogs", status = NOTEBOOK_STATUS_RUNNING, updateTimestamp=dt.datetime.now() - dt.timedelta(seconds=100))
    mocker.patch("utils.kubernetesAPI.KubernetesAPI.getPodStatus", return_value = "PENDING")
    orphanJobsChecker()
    assert NotebookRunLogs.objects.get(pk=notebookRunLogs.id).status == NOTEBOOK_STATUS_RUNNING

    workflow = mixer.blend("workflows.workflow", periodictask=None)
    workflowRun = mixer.blend("workflows.workflowRun", status=STATUS_RUNNING, workflow=workflow)
    notebookRunLogs = mixer.blend("genie.notebookRunLogs", workflowRun=workflowRun, status=NOTEBOOK_STATUS_RUNNING)
    orphanJobsChecker()
    assert WorkflowRun.objects.get(id=workflowRun.id).status == STATUS_RUNNING
    
    notebookRunLogs.status = NOTEBOOK_STATUS_SUCCESS
    notebookRunLogs.save()
    orphanJobsChecker()
    assert WorkflowRun.objects.get(id=workflowRun.id).status == STATUS_SUCCESS

    workflowRun.status = STATUS_RUNNING
    workflowRun.save()
    notebookRunLogs.status = NOTEBOOK_STATUS_ERROR
    notebookRunLogs.save()
    orphanJobsChecker()
    assert WorkflowRun.objects.get(id=workflowRun.id).status == STATUS_ERROR
