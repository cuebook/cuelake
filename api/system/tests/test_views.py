import pytest
import unittest
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from conftest import populate_seed_data

from system.models import AccountSetting, AccountSettingValue
from collections import OrderedDict


@pytest.mark.django_db
def test_getAccountSettings(client, populate_seed_data, mocker):
    path = reverse('accountSettingView')
    AccountSetting.objects.create(key="xxx", label="test")
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data == {'success': True, 'message': 'Fetched account settings successfully', 'data': [OrderedDict([('key', 'notifyOnSuccess'), ('label', 'Notify on Success'), ('type', 'bool'), ('value', '')]), OrderedDict([('key', 'notifyOnFailure'), ('label', 'Notify on Failure'), ('type', 'bool'), ('value', '')]), OrderedDict([('key', 'slackWebhookUrl'), ('label', 'Slack Webhook URL'), ('type', 'text'), ('value', '')]), OrderedDict([('key', 'xxx'), ('label', 'test'), ('type', 'text'), ('value', '')])]}


@pytest.mark.django_db
def test_updateAccountSettings(client, populate_seed_data, mocker):
    path = reverse('accountSettingView')
    AccountSetting.objects.create(key="xxx", label="test")
    data = [{"key": "xxx", "value": "yyy"}]
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert AccountSettingValue.objects.filter(value="yyy").count() == 1

