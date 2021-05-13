import asyncio
import json
import aiohttp
import requests
from django.conf import settings
from rest_framework import response

NOTEBOOKS_ENDPOINT = "api/notebook"
NOTEBOOK_STATUS_ENDPOINT = "api/notebook/job"

class ZeppelinAPI:
    """
    Functionalities around zeppelin APIs
    """
    def getAllNotebooks(self):
        """
        Return all notebooks from zeppelin
        """
        response = requests.get(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}")
        return self.__parseResponse(response)

    async def getNotebookStatus(self, notebookId: str):
        """
        Async method to return status of all paragraphs from a notebook
        """
        url = f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOK_STATUS_ENDPOINT}/{notebookId}"
        defaultResponse = {"id": notebookId}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    responseJSON = await response.json() 
                    if responseJSON["status"] == "OK":
                        return responseJSON["body"]
                    else:
                        return defaultResponse
        except Exception as ex:
            return defaultResponse


    def getNotebookDetails(self, notebookId: str):
        """
        Return all paragraphs from a notebook
        """
        response = requests.get(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/{notebookId}")
        return self.__parseResponse(response)

    def runNotebookJob(self, notebookId: str):
        """
        Run all paragraphs from a notebook
        """
        response = requests.post(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/job/{notebookId}")
        return self.__parseResponse(response)

    def stopNotebookJob(self, notebookId: str):
        """
        Stop all paragraphs from a notebook
        """
        response = requests.delete(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/job/{notebookId}")
        return self.__parseResponse(response)

    def clearNotebookResults(self, notebookId: str):
        """
        Clear all paragraph results from a notebook
        """
        response = requests.put(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/{notebookId}/clear")
        return self.__parseResponse(response)

    def addNotebook(self, notebook: dict):
        """
        Clear all paragraph results from a notebook
        """
        response = requests.post(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}", notebook)
        return self.__parseResponse(response)

    def cloneNotebook(self, notebookId: str, payload: dict):
        """
        Clear all paragraph results from a notebook
        """
        response = requests.post(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/{notebookId}", payload)
        print(response.json())
        print(payload)
        return self.__parseResponse(response)

    def deleteNotebook(self, notebookId: str):
        """
        Clear all paragraph results from a notebook
        """
        response = requests.delete(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/{notebookId}")
        return self.__parseResponse(response)
    
    def updateNotebookParagraphs(self, notebookId: str, notebook: dict):
        """
        Updates zeppelin notebook paragraphs with new notebook
        """
        oldParagraphs = [para["id"] for para in self.getNotebookDetails(notebookId)["paragraphs"]]
        for paraId in oldParagraphs:
            requests.delete(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/{notebookId}/paragraph/{paraId}")
        newParagraphs = json.loads(notebook)["paragraphs"]
        for para in newParagraphs:
            requests.post(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/{notebookId}/paragraph", json.dumps(para))
        return True
    
    def renameNotebook(self, notebookId: str, newName: str):
        """
        Renames zeppelin notebook
        """
        response = requests.put(f"{settings.ZEPPELIN_HOST}:{settings.ZEPPELIN_PORT}/{NOTEBOOKS_ENDPOINT}/{notebookId}/rename", json.dumps({"name": newName}))
        return self.__parseResponse(response)

    def __parseResponse(self, response):
        """
        Parses the response returned by zeppelin APIs
        """
        try:
            responseJSON = response.json()
            if responseJSON["status"] == "OK":
                return responseJSON.get("body", True)
            else:
                return False
        except Exception as ex:
            return False

# Export initalized class
Zeppelin = ZeppelinAPI()