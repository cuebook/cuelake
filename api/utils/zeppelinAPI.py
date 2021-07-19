import asyncio
import logging
import time
import json
import aiohttp
import requests
from django.conf import settings
from rest_framework import response

# Get an instance of a logger
logger = logging.getLogger(__name__)

NOTEBOOKS_ENDPOINT = "api/notebook"
NOTEBOOK_STATUS_ENDPOINT = "api/notebook/job"
INTERPRETER_RESTART_ENDPOINT = "api/interpreter/setting/restart"
ZEPPELIN_API_RETRY_COUNT = 3
ZEPPELIN_VERSION_ENDPOINT = "api/version"

class ZeppelinAPI:
    """
    Functionalities around zeppelin APIs
    """
    ZEPPELIN_ADDR = settings.ZEPPELIN_HOST + ":" + settings.ZEPPELIN_PORT

    def __init__(self, zeppelinServerId: str = None):
        if(zeppelinServerId):
            self.ZEPPELIN_ADDR = "http://" + zeppelinServerId + ":" + settings.ZEPPELIN_PORT

    def setZeppelinAddress(self, host: str, port: str):
        self.ZEPPELIN_ADDR = "http://"+ host + ":" + port

    def getAllNotebooks(self, folder=""):
        """
        Return all notebooks from zeppelin
        """
        response = requests.get(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}")
        data = self.__parseResponse(response)
        data = [ x for x in data if x['path'].split("/")[-2]==folder ]
        return data

    async def getNotebookStatus(self, notebookId: str):
        """
        Async method to return status of all paragraphs from a notebook
        """
        url = f"{self.ZEPPELIN_ADDR}/{NOTEBOOK_STATUS_ENDPOINT}/{notebookId}"
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
        response = requests.get(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/{notebookId}")
        return self.__parseResponse(response)

    def getNotebookDetailsWithRetry(self, notebookId: str, retryCount: int = 0):
        response = self.getNotebookDetails(notebookId)
        if response:
            return response
        else:
            if retryCount < ZEPPELIN_API_RETRY_COUNT:
                return self.getNotebookDetailsWithRetry(notebookId, retryCount + 1)
            else:
                return False

    def runNotebookJob(self, notebookId: str):
        """
        Run all paragraphs from a notebook
        """
        response = requests.post(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/job/{notebookId}")
        return self.__parseResponse(response)

    def stopNotebookJob(self, notebookId: str):
        """
        Stop all paragraphs from a notebook
        """
        isNotebookRunning = True
        while isNotebookRunning:
            requests.delete(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/job/{notebookId}")
            response = self.getNotebookDetailsWithRetry(notebookId)
            isNotebookRunning = response.get("info", {}).get("isRunning", False)
            time.sleep(3)

        logger.info(f"Stop notebook {notebookId}")
        return self.__parseResponse(response)

    def clearNotebookResults(self, notebookId: str):
        """
        Clear all paragraph results from a notebook
        """
        response = requests.put(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/{notebookId}/clear")
        logger.info(f"Clear notebook {notebookId}")
        logger.info(f"Clear notebook response {response.json()}")
        return self.__parseResponse(response)

    def addNotebook(self, notebook: dict):
        """
        Clear all paragraph results from a notebook
        """
        response = requests.post(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}", notebook)
        return self.__parseResponse(response)

    def cloneNotebook(self, notebookId: str, payload: dict):
        """
        Clear all paragraph results from a notebook
        """
        response = requests.post(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/{notebookId}", payload)
        return self.__parseResponse(response)

    def deleteNotebook(self, notebookId: str):
        """
        Clear all paragraph results from a notebook
        """
        response = requests.delete(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/{notebookId}")
        return self.__parseResponse(response)
    
    def updateNotebookParagraphs(self, notebookId: str, notebook: dict):
        """
        Updates zeppelin notebook paragraphs with new notebook
        """
        oldParagraphs = [para["id"] for para in self.getNotebookDetails(notebookId)["paragraphs"]]
        for paraId in oldParagraphs:
            requests.delete(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/{notebookId}/paragraph/{paraId}")
        newParagraphs = json.loads(notebook)["paragraphs"]
        for para in newParagraphs:
            requests.post(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/{notebookId}/paragraph", json.dumps(para))
        return True
    
    def renameNotebook(self, notebookId: str, newName: str):
        """
        Renames zeppelin notebook
        """
        response = requests.put(f"{self.ZEPPELIN_ADDR}/{NOTEBOOKS_ENDPOINT}/{notebookId}/rename", json.dumps({"name": newName}))
        x = self.__parseResponse(response)
        return x

    def restartInterpreter(self, interpreterName: str):
        """
        Restarts interpreter
        """
        response = requests.put(f"{self.ZEPPELIN_ADDR}/{INTERPRETER_RESTART_ENDPOINT}/{interpreterName}")
        return self.__parseResponse(response)

    def healthCheck(self):
        try:
            response = requests.get(f"{self.ZEPPELIN_ADDR}/{ZEPPELIN_VERSION_ENDPOINT}")
            return self.__parseResponse(response)
        except Exception as ex:
            return False

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
