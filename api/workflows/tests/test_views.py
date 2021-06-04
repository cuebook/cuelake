import pytest
import unittest
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from conftest import populate_seed_data

from genie.services import NotebookJobServices


@pytest.mark.django_db(transaction=True)
def test_workflows(client, populate_seed_data):

	# ======================= create workflow test =======================
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

	# ======================= update workflow test ======================
	path = reverse('workflowsPost')
	data = {'id': workflowId,
			 'name': 'testWorkflow',
			 'notebookIds': ['2G5CNGNAJ'],
			 'scheduleId': None,
			 'triggerWorkflowId': None,
			 'triggerWorkflowStatus': 'ALWAYS'}

	response = client.post(path, data=data, content_type="application/json")
	assert response.status_code == 200
	assert response.data['data']


	# ======================= get workflows test =========================

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


	# ===================== assign schedule test =========================

	res = NotebookJobServices.addSchedule(cron="* 34 * * *", timezone="Africa/Asmara", name="testSchedule")
	assert res.data
	scheduleId = res.data

	path = reverse('updateSchedule', kwargs={"workflowId": workflowId})
	data = {"scheduleId": scheduleId}

	response = client.post(path, data=data, content_type="application/json")
	assert response.status_code == 200
	assert response.data['data']

	

	# ===================== assign trigger workflow test =========================

	# creating workflow
	path = reverse('workflowsPost')
	data = {'name': 'triggerWorkflow',
			 'notebookIds': [],
			 'scheduleId': None,
			 'triggerWorkflowId': None,
			 'triggerWorkflowStatus': 'ALWAYS'}
	response = client.post(path, data=data, content_type="application/json")
	assert response.status_code == 200
	assert response.data['data']

	_workflowId = response.data['data']
	# assigning it as trigger workflow

	path = reverse('updateTriggerWorkflow', kwargs={"workflowId": workflowId})
	data = {
		"triggerWorkflowId": _workflowId,
		"triggerWorkflowStatus": "SUCCESS"
	}

	response = client.post(path, data=data, content_type="application/json")
	assert response.status_code == 200
	assert response.data['data'] == 1


	# getting workflows test 

	path = reverse('workflows', kwargs={"offset": 0})
	response = client.get(path)

	exceptedWorkflows = [{'id': _workflowId,
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
						   'triggerWorkflowStatus': 'SUCCESS'}]


	assert response.status_code == 200
	assert response.data['data']['total'] == 2
	case = unittest.TestCase()
	case.assertListEqual(response.data['data']['workflows'], exceptedWorkflows)



	# ======================= delete workflow test ==========================

	path =  reverse("workflow", kwargs={"workflowId": _workflowId})
	response = client.delete(path)
	assert response.status_code == 200
	assert response.data['success']


	# ======================== get workflowRuns test ==========================
	path = reverse("workflowRuns", kwargs={"workflowId": workflowId, "offset": 0})
	response = client.get(path)
	assert response.status_code == 200
	assert response.data['data'] == {'total': 0, 'workflowRuns': []}


	# ======================== runWorkflow test ===============================
	# path =  reverse("runWorkflow", kwargs={"workflowId": workflowId})
	# response = client.get(path)
	# assert response.status_code == 200


	# ======================== get workflowRuns test ==========================