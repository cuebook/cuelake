import pytest
import unittest
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from conftest import populate_seed_data

from system.models import AccountSetting, AccountSettingValue
from system.services import NotificationServices, AccountSettingServices
from collections import OrderedDict


@pytest.mark.django_db
def test_notify(client, populate_seed_data, mocker):
    path = reverse('accountSettingView')
    notebookName = "testNotebook"
    accs = AccountSetting.objects.get(key="notifyOnSuccess")
    AccountSettingValue.objects.create(accountSetting=accs, value="true")
    mocker.patch("requests.post", return_value = None)
    NotificationServices.notify(notebookName=notebookName, isSuccess=True, message="Successful")
    

@pytest.mark.django_db
def test_getAccountSetting(client, populate_seed_data, mocker):
    res = AccountSettingServices.getAccountSetting(key="xxx")
    assert not res.success
    accs = AccountSetting.objects.get(key="notifyOnSuccess")
    AccountSettingValue.objects.create(accountSetting=accs, value="true")
    res = AccountSettingServices.getAccountSetting(key="notifyOnSuccess")
    assert res.success

