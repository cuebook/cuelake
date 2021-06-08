import pytest
import unittest
from unittest import mock
from django.test import TestCase
from datetime import datetime
from django.urls import reverse
from mixer.backend.django import mixer
from django.conf import settings

S3_FILES_PREFIX = settings.S3_FILES_PREFIX

@pytest.mark.django_db(transaction=True)
def test_getFiles(client, mocker):
    """
    Test if get files api 
    """
    expectedListObjects = {
        'IsTruncated': True,
        'Contents': [
            {
                'Key': S3_FILES_PREFIX + 'string',
                'LastModified': datetime(2015, 1, 1),
                'ETag': 'string',
                'Size': 123,
                'StorageClass': 'STANDARD',
                'Owner': {
                    'DisplayName': 'string',
                    'ID': 'string'
                }
            },
            {
                'Key': S3_FILES_PREFIX + 'str',
                'LastModified': datetime(2015, 1, 1),
                'ETag': 'str',
                'Size': 123,
                'StorageClass': 'OUTPOSTS',
                'Owner': {
                    'DisplayName': 'str',
                    'ID': 'str'
                }
            },
        ],
        'Name': 'string',
        'Prefix': 'string',
        'Delimiter': 'string',
        'MaxKeys': 123,
        'CommonPrefixes': [
            {
                'Prefix': 'string'
            },
        ],
        'EncodingType': 'url',
        'KeyCount': 123,
        'ContinuationToken': 'string',
        'NextContinuationToken': 'string',
        'StartAfter': 'string'
    }
    class mockedBotoClient:
        def __init__(self, *args, **kwargs):
            print("mocker boto client")

        def list_objects_v2(*args, **kwargs):
            return expectedListObjects


    listObjectsV2Patch = mocker.patch("boto3.client", new=mock.MagicMock(autospec=True, side_effect=mockedBotoClient))
    listObjectsV2Patch.start()

    path = reverse("files", kwargs={"offset": 0})
    response = client.get(path)

    assert response.status_code == 200
    assert response.data['data'] == [{'Key': 'string',
          'LastModified': datetime(2015, 1, 1, 0, 0),
          'Size': 123},
         {'Key': 'str',
          'LastModified': datetime(2015, 1, 1, 0, 0),
          'Size': 123}]

    listObjectsV2Patch.stop()


# @pytest.mark.django_db(transaction=True)
# def test_uploadFile(client, mocker):
#   """
#   Tests upload file api 
#   """

# @pytest.mark.django_db(transaction=True)
# def test_deleteFiles(client, mocker):
#   """
#   Test if get files api 
#   """