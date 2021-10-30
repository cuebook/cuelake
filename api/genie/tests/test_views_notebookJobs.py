import pytest
import unittest
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from conftest import populate_seed_data

from genie.services import NotebookJobServices

from genie.models import NotebookObject
from genie.tasks import NotebookRunLogs


@pytest.mark.django_db
def test_getNotebooks(client, populate_seed_data, mocker):
    path = reverse('notebooks', kwargs={"offset": 0, "workspaceId": 1})
    mixer.blend("workspace.workspace", id=1, name="test")
    mocker.patch("utils.zeppelinAPI.ZeppelinAPI.getAllNotebooks", return_value = [{"path": "notebook", "id": "BX976MDDE"}])
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['data']["count"]  == 1
    assert response.data['data']["notebooks"]  == [{'path': 'notebook', 'id': 'BX976MDDE', 'name': 'notebook', 'isScheduled': False, 'assignedWorkflow': []}]


@pytest.mark.django_db
def test_addNotebook(client, populate_seed_data, mocker):
    path = reverse('notebook', kwargs={"workspaceId": 1})
    mixer.blend("workspace.workspace", id=1, name="test")
    data = {"notebookTemplateId": 1}
    mixer.blend("genie.notebookTemplate")
    mocker.patch("utils.zeppelinAPI.ZeppelinAPI.addNotebook", return_value = True)
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    print(response.data)
    assert response.data['success']  == True
    assert NotebookObject.objects.count() == 1

@pytest.mark.django_db
def test_notebooksLightView(client, populate_seed_data, mocker):
    path = reverse('notebooksLightView', kwargs={"workspaceId": 1})
    mixer.blend("workspace.workspace", id=1, name="test")
    mocker.patch("utils.zeppelinAPI.ZeppelinAPI.getAllNotebooks", return_value = [{"path": "notebook", "id": "BX976MDDE"}])
    response = client.get(path, content_type="application/json")
    print(response.data['data'])
    assert response.status_code == 200
    assert response.data['data'] == [{'path': 'notebook', 'id': 'BX976MDDE'}]

@pytest.mark.django_db
def test_cloneNotebook(client, populate_seed_data, mocker):
    path = reverse('notebookOperations', kwargs={"notebookId": "BX976MDDE", "workspaceId": 1})
    mixer.blend("workspace.workspace", id=1, name="test")
    mocker.patch("utils.zeppelinAPI.ZeppelinAPI.cloneNotebook", return_value = True)
    response = client.post(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True

@pytest.mark.django_db
def test_deleteNotebook(client, populate_seed_data, mocker):
    path = reverse('notebookOperations', kwargs={"notebookId": "BX976MDDE", "workspaceId": 1})
    mixer.blend("workspace.workspace", id=1, name="test")
    mocker.patch("utils.zeppelinAPI.ZeppelinAPI.deleteNotebook", return_value = True)
    response = client.delete(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True

@pytest.mark.django_db
def test_runAndStopNotebookJob(client, populate_seed_data, mocker):
    path = reverse('notebookActions', kwargs={"notebookId": "BX976MDDE", "workspaceId": 1})
    mixer.blend("workspace.workspace", id=1, name="test")
    mocker.patch("genie.tasks.runNotebookJob.delay", auto_spec=True)
    response = client.post(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True
    mocker.patch("utils.zeppelinAPI.ZeppelinAPI.stopNotebookJob", return_value = True)
    response = client.delete(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True

@pytest.mark.django_db
def test_clearNotebookResults(client, populate_seed_data, mocker):
    path = reverse('notebookActions', kwargs={"notebookId": "BX976MDDE", "workspaceId": 1})
    mixer.blend("workspace.workspace", id=1, name="test")
    mocker.patch("utils.zeppelinAPI.ZeppelinAPI.clearNotebookResults", return_value = True)
    response = client.put(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True

@pytest.mark.django_db
def test_getNotebookJobs(client, populate_seed_data, mocker):
    path = reverse('notebookJobView', kwargs={"notebookId": "BX976MDDE"})
    mixer.blend("genie.notebookRunLogs", notebookId="BX976MDDE")
    mocker.patch("utils.zeppelinAPI.ZeppelinAPI.clearNotebookResults", return_value = True)
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True
    assert len(response.data["data"]["notebookRunLogs"]) == 1
    assert response.data["data"]["count"] == 1

@pytest.mark.django_db
def test_notebookJob(client, populate_seed_data, mocker):
    path = reverse('notebooksJobView')
    data = {"notebookId": "BX976MDDE", "scheduleId": 1}
    mixer.blend("genie.customSchedule", id=1)
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True

    # Test delete notebook job
    response = client.delete(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True

