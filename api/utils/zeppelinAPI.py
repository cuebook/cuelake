import requests
from django.conf import settings
from rest_framework import response

NOTEBOOKS_ENDPOINT = "api/notebook"
NOTEBOOK_STATUS_ENDPOINT = "api/notebook/job/"

class ZeppelinAPI:
    """
    Functionalities around zeppelin APIs
    """
    def getAllNotebooks(self):
        """
        Return all notebooks from zeppelin
        """
        response = requests.get(settings.ZEPPELIN_HOST + ":" + settings.ZEPPELIN_PORT + "/" + NOTEBOOKS_ENDPOINT)
        return self.__parseResponse(response)

    def getNotebookStatus(self, notebookId: str):
        """
        Return status of all paragraphs from a notebook
        """
        response = requests.get(settings.ZEPPELIN_HOST + ":" + settings.ZEPPELIN_PORT + "/" + NOTEBOOK_STATUS_ENDPOINT + "/" + notebookId)
        return self.__parseResponse(response)

    def getNotebookDetails(self, notebookId: str):
        """
        Return all paragraphs from a notebook
        """
        response = requests.get(settings.ZEPPELIN_HOST + ":" + settings.ZEPPELIN_PORT + "/" + NOTEBOOKS_ENDPOINT + "/" + notebookId)
        return self.__parseResponse(response)

    def __parseResponse(self, response):
        """
        Parses the response returned by zeppelin APIs
        """
        try:
            responseJSON = response.json()
            if responseJSON["status"] == "OK":
                return responseJSON["body"]
            else:
                return False
        except Exception as ex:
            return False
