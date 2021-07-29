import pytest
import unittest
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from conftest import populate_seed_data

from genie.services import ScheduleService
from workflows.tasks import runWorkflowJob
from genie.tasks import runNotebookJob

from workflows.models import WorkflowRunLogs, STATUS_ERROR, STATUS_SUCCESS
from genie.tasks import NotebookRunLogs


@pytest.mark.django_db(transaction=True)
def test_workflows(client, populate_seed_data, mocker):

    # Create workflow test
    path = reverse('workflowsPost')
    data = {'name': 'test',
             'notebookIds': [],
             'scheduleId': None,
             'triggerWorkflowId': None,
             'triggerWorkflowStatus': 'ALWAYS'}
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['data']
    workflowId = response.data['data']

    # Update workflow test
    path = reverse('workflowsPost')
    data = {'id': workflowId,
             'name': 'testWorkflow',
             'notebookIds': ['2G5CNGNAJ'],
             'scheduleId': None,
             'triggerWorkflowId': None,
             'triggerWorkflowStatus': 'ALWAYS'}
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success']

    # Get workflows test
    path = reverse('workflows', kwargs={"offset": 0})
    response = client.get(path)
    exceptedWorkflow = {'id': workflowId,
                         'lastRun': None,
                         'name': 'testWorkflow',
                         'notebooks': ['2G5CNGNAJ'],
                         'schedule': None,
                         'triggerWorkflow': None,
                         'triggerWorkflowStatus': 'ALWAYS'}
    assert response.status_code == 200
    assert response.data['data']['total'] == 1
    assert response.data['data']['workflows'][0] == exceptedWorkflow


    # Assign schedule test
    res = ScheduleService.addSchedule(cron="* 34 * * *", timezone="Africa/Asmara", name="testSchedule")
    assert res.data
    scheduleId = res.data
    path = reverse('updateSchedule', kwargs={"workflowId": workflowId})
    data = {"scheduleId": scheduleId}
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['data']

    # Assign trigger workflow test
    path = reverse('workflowsPost')
    data = {'name': 'triggerWorkflow',
             'notebookIds': [],
             'scheduleId': None,
             'triggerWorkflowId': None,
             'triggerWorkflowStatus': 'ALWAYS'}
    # Creating workflow
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['data']
    _workflowId = response.data['data']

    # Assigning it as trigger workflow
    path = reverse('updateTriggerWorkflow', kwargs={"workflowId": workflowId})
    data = {
        "triggerWorkflowId": _workflowId,
        "triggerWorkflowStatus": STATUS_SUCCESS
    }
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['data'] == 1

    # Getting workflows test 
    path = reverse('workflows', kwargs={"offset": 0})
    response = client.get(path)
    expectedWorkflows = [{'id': _workflowId,
                           'lastRun': None,
                           'name': 'triggerWorkflow',
                           'notebooks': [],
                           'schedule': None,
                           'triggerWorkflow': None,
                           'triggerWorkflowStatus': 'ALWAYS'},
                          {'id': workflowId,
                           'lastRun': None,
                           'name': 'testWorkflow',
                           'notebooks': ['2G5CNGNAJ'],
                           'schedule': {'id': scheduleId, 'name': 'testSchedule'},
                           'triggerWorkflow': {'id': _workflowId, 'name': 'triggerWorkflow'},
                           'triggerWorkflowStatus': STATUS_SUCCESS}]
    assert response.status_code == 200
    assert response.data['data']['total'] == 2
    case = unittest.TestCase()
    case.assertListEqual(response.data['data']['workflows'], expectedWorkflows)

    # Run workflow test
    runWorkflowJobPatch = mocker.patch("workflows.tasks.runWorkflowJob.delay", new=mock.MagicMock(autospec=True, side_effect=runWorkflowJob))
    runNotebookJobPatch = mocker.patch("genie.tasks.runNotebookJob.delay", new=mock.MagicMock(autospec=True, side_effect=runNotebookJob))
    runNotebookJobPatch.start()
    runWorkflowJobPatch.start()
    path =  reverse("runWorkflow", kwargs={"workflowId": _workflowId})
    response = client.get(path)
    assert response.status_code == 200
    assert WorkflowRunLogs.objects.count() == 2
    assert NotebookRunLogs.objects.count() == 1
    runWorkflowJobPatch.stop()
    runNotebookJobPatch.stop()

    # Get workflow test
    path = reverse('workflows', kwargs={"offset": 0})
    response = client.get(path)
    expectedLastRunKeys = set(["endTimestamp", "startTimestamp", "status", "workflowRunId"])
    assert response.status_code == 200
    assert response.data['data']['total'] == 2
    assert set(response.data['data']['workflows'][0]['lastRun'].keys()) == expectedLastRunKeys
    assert set(response.data['data']['workflows'][1]['lastRun'].keys()) == expectedLastRunKeys

    # Sorting on workflows test
    path = reverse('workflowsPost')
    data = {'name': 'sortTest',
             'notebookIds': [],
             'scheduleId': None,
             'triggerWorkflowId': workflowId,
             'triggerWorkflowStatus': 'ALWAYS'}
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['data']

    # Sort on name test
    path = reverse("workflows", kwargs={"offset": 0}) + "?sortColumn=name&sortOrder=descend"
    response = client.get(path)
    names = [ x['name'] for x in response.data['data']['workflows'] ] 
    assert names == sorted(names, reverse=True)

    path = reverse("workflows", kwargs={"offset": 0}) + "?sortColumn=name&sortOrder=ascend"
    response = client.get(path)
    names = [ x['name'] for x in response.data['data']['workflows'] ] 
    assert names == sorted(names)

    # Sort on trigger workflow name test
    path = reverse("workflows", kwargs={"offset": 0}) + "?sortColumn=triggerWorkflow&sortOrder=descend"
    response = client.get(path)
    triggerWorkflows = [ x['triggerWorkflow']['name'] for x in response.data['data']['workflows'] if x['triggerWorkflow'] ] 
    assert triggerWorkflows == sorted(triggerWorkflows, reverse=True)

    path = reverse("workflows", kwargs={"offset": 0}) + "?sortColumn=triggerWorkflow&sortOrder=ascend"
    response = client.get(path)
    triggerWorkflows = [ x['triggerWorkflow']['name'] for x in response.data['data']['workflows'] if x['triggerWorkflow'] ] 
    assert triggerWorkflows == sorted(triggerWorkflows)

    # Sort on last run time test
    # path = reverse("workflows", kwargs={"offset": 0}) + "?sortColumn=lastRunTime&sortOrder=descend"
    # response = client.get(path)
    # lastRunTimestamps = [ x['lastRun']['startTimestamp'] for x in response.data['data']['workflows'] if x['lastRun']] 
    # assert lastRunTimestamps == sorted(lastRunTimestamps, reverse=True)

    # path = reverse("workflows", kwargs={"offset": 0}) + "?sortColumn=lastRunTime&sortOrder=ascend"
    # response = client.get(path)
    # lastRunTimestamps = [ x['lastRun']['startTimestamp'] for x in response.data['data']['workflows'] if x['lastRun']] 
    # assert lastRunTimestamps == sorted(lastRunTimestamps)


    # Delete workflow test
    path =  reverse("workflow", kwargs={"workflowId": _workflowId})
    response = client.delete(path)
    assert response.status_code == 200
    assert response.data['success']

    # Get workflowRuns test
    path = reverse("workflowRuns", kwargs={"workflowId": workflowId, "offset": 0})
    response = client.get(path)
    assert response.status_code == 200
    assert response.data['data']['total'] == 1
    assert set(response.data['data']['workflowRuns'][0].keys()) == set(["endTimestamp", "id", "startTimestamp", "status", "workflow"])
