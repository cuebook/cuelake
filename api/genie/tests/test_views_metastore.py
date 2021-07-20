import pytest
from unittest import mock
from django.urls import reverse
from mixer.backend.django import mixer
from conftest import populate_seed_data


@pytest.mark.django_db
def test_getMetastoreTables(client, populate_seed_data, mocker):
    path = reverse('metastoreTables')
    mocker.patch("psycopg2.connect")
    mocker.patch("genie.services.Metastore.executeSQL", return_value = [
        {"id": 1, "table": "testtable", "type": "VIRTUAL_VIEW", "database": "default", "size": None, "last_updated": "1620749748"},
        {"id": 1, "table": "testtable2", "type": "EXTERNAL_TABLE", "database": "default", "size": 233434, "last_updated": "1620749748"}
    ])
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True
    assert response.data['data'] == {'default': {'views': [{'id': 1, 'table': 'testtable', 'type': 'VIRTUAL_VIEW', 'database': 'default', 'size': None, 'last_updated': '1620749748'}], 'tables': [{'id': 1, 'table': 'testtable2', 'type': 'EXTERNAL_TABLE', 'database': 'default', 'size': 233434, 'last_updated': '1620749748'}]}}

@pytest.mark.django_db
def test_getMetastoreColumns(client, populate_seed_data, mocker):
    path = reverse('metastoreColumns', kwargs={"tableId": 1})
    mocker.patch("psycopg2.connect")
    mocker.patch("genie.services.Metastore.executeSQL", return_value = [
        {"name": "Col", "tableId": 1, "type": "decimal"},
        {"name": "Col2", "tableId": 1, "type": "decimal"},
    ])
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data['success'] == True
    assert response.data['data'] == [{'name': 'Col', 'tableId': 1, 'type': 'decimal'}, {'name': 'Col2', 'tableId': 1, 'type': 'decimal'}]