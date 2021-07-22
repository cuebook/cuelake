import pytest
import datetime as dt
from unittest import mock
from django.urls import reverse
from genie.models import RunStatus, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_SUCCESS, NOTEBOOK_STATUS_ERROR
from workflows.models import WorkflowRun, STATUS_RUNNING, STATUS_SUCCESS, STATUS_ERROR
from mixer.backend.django import mixer
from conftest import populate_seed_data
from genie.routineTasks import orphanJobsChecker


@pytest.mark.django_db
def test_getMetastoreTables(client, populate_seed_data, mocker):
    runStatus = mixer.blend("genie.runStatus", status = NOTEBOOK_STATUS_RUNNING, updateTimestamp=dt.datetime.now() - dt.timedelta(seconds=100))
    mocker.patch("utils.kubernetesAPI.KubernetesAPI.getPodStatus", return_value = "PENDING")
    orphanJobsChecker()
    assert RunStatus.objects.get(pk=runStatus.id).status == NOTEBOOK_STATUS_RUNNING

    workflow = mixer.blend("workflows.workflow", periodictask=None)
    workflowRun = mixer.blend("workflows.workflowRun", status=STATUS_RUNNING, workflow=workflow)
    runStatus = mixer.blend("genie.runStatus", workflowRun=workflowRun, status=NOTEBOOK_STATUS_RUNNING)
    orphanJobsChecker()
    assert WorkflowRun.objects.get(id=workflowRun.id).status == STATUS_RUNNING
    
    runStatus.status = NOTEBOOK_STATUS_SUCCESS
    runStatus.save()
    orphanJobsChecker()
    assert WorkflowRun.objects.get(id=workflowRun.id).status == STATUS_SUCCESS

    workflowRun.status = STATUS_RUNNING
    workflowRun.save()
    runStatus.status = NOTEBOOK_STATUS_ERROR
    runStatus.save()
    orphanJobsChecker()
    assert WorkflowRun.objects.get(id=workflowRun.id).status == STATUS_ERROR
