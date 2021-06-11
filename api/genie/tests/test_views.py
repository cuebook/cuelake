from django.test import TestCase
import pytest
import unittest
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from conftest import populate_seed_data
from genie.models import CustomSchedule as Schedule

@pytest.mark.django_db(transaction=True)
def test_schedules(client, populate_seed_data, mocker):

    # ======================= create schedule test =======================
    path = reverse('scheduleView')
    data = {'name': 'Schedule at 3 AM ',
             'crontab': '0 3 * * *',
             'timezone':'Asia/Kolkata' }

    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data['data']
    scheduleId = response.data["data"]

     # ======================= update schedule test ======================
    path = reverse('scheduleView')
    data = {'id': scheduleId,
             'name': 'Schedule at 4 AM ',
             'crontab': '0 4 * * *',
             'timezone': 'Asia/Kolkata'}
    response = client.put(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert Schedule.objects.get(id=scheduleId).name == "Schedule at 4 AM "

    # ======================= get schedule test =========================
    path = reverse('scheduleView')
    response = client.get(path)
    assert response.status_code == 200
    assert response.data["data"]

    # ======================= getSingleSchedule test =====================
    path = reverse("getSingleSchedule", kwargs={"scheduleId": scheduleId})
    response = client.get(path)
    assert response.status_code == 200
    assert response.data["data"]
    assert response.data["data"][0]["name"] == "Schedule at 4 AM "

    # ======================= delete SingleSchedule test =====================
    path = reverse("getSingleSchedule", kwargs={"scheduleId": scheduleId})
    response = client.delete(path)
    assert response.status_code == 200
    assert Schedule.objects.filter(id=scheduleId).count() == 0
