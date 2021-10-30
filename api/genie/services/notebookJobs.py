from utils.helperFunctions import helperFunctions
import asyncio
import json
import pytz
import time
import logging
import threading
from typing import List
from django.template import Template, Context
from genie.models import NOTEBOOK_STATUS_ABORT, NOTEBOOK_STATUS_QUEUED, NOTEBOOK_STATUS_RUNNING, NotebookObject, NotebookJob, NotebookRunLogs, Connection, NotebookTemplate, CustomSchedule as Schedule
from genie.serializers import NotebookObjectSerializer, NotebookRunLogsSerializer
from workflows.models import Workflow, WorkflowNotebookMap
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import ZeppelinAPI
from genie.tasks import runNotebookJob as runNotebookJobTask
from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"

GET_NOTEBOOKOJECTS_LIMIT = 25
RUN_STATUS_LIMIT = 10

class NotebookJobServices:
    """
    Class containing services related to NotebookJob model
    """    
    @staticmethod
    async def _fetchNotebookStatuses(notebooks: list, workspaceId: int = 0):
        """
        Async method to fetch notebook status details for multiple notebooks
        Returns a dict with notebook ids as keys
        :param notebooks: List of notebook describing dicts each containing the 'id' field
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        notebookStatuses = {}
        for future in asyncio.as_completed([ZeppelinAPI(workspaceName).getNotebookStatus(notebook["id"]) for notebook in notebooks]):
            status = await future
            notebookStatuses[status["id"]] = status
        return notebookStatuses

    @staticmethod
    def getNotebooks(offset: int = 0, limit: int = None , searchQuery: str = None, sorter: dict = None, _filter: dict = None, workspaceId: int = 0):
        """
        Service to fetch and serialize NotebookJob objects
        Number of NotebookObjects fetched is stored as the constant GET_NOTEBOOKOJECTS_LIMIT
        :param offset: Offset for fetching NotebookJob objects
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error retrieving notebooks")
        notebooks =  ZeppelinAPI(workspaceName).getAllNotebooks()
        if searchQuery:
            notebooks = NotebookJobServices.search(notebooks, "path", searchQuery)
        if sorter.get('order', False):
            notebooks = NotebookJobServices.sortingOnNotebook(notebooks, sorter, _filter)
        if notebooks:
            notebookCount = len(notebooks)
            notebooks = notebooks[offset: offset + GET_NOTEBOOKOJECTS_LIMIT]
            notebookIds = [notebook["id"] for notebook in notebooks]
            notebookObjects = NotebookObject.objects.filter(notebookZeppelinId__in=notebookIds)
            notebookJobs = NotebookJob.objects.filter(notebookId__in=notebookIds)
            for notebook in notebooks:
                notebook["name"] = notebook["path"]
                notebookObj = next((notebookObj for notebookObj in notebookObjects if notebookObj.notebookZeppelinId == notebook["id"]), False)
                if notebookObj:
                    notebook["notebookObjId"] = notebookObj.id
                notebookJob = next((notebookJob for notebookJob in notebookJobs if notebookJob.notebookId == notebook["id"]), False)
                if notebookJob:
                    notebook["isScheduled"] = True
                    notebook["schedule"] = str(notebookJob.crontab.customschedule.name)
                    notebook["isActive"] = notebookJob.enabled
                    notebook["notebookJobId"] = notebookJob.id
                else:
                    notebook["isScheduled"] = False
            
                assignedWorkflowId = WorkflowNotebookMap.objects.filter(notebookId = notebook["id"]).values_list("workflow_id", flat=True)
                names= Workflow.objects.filter(id__in = assignedWorkflowId).values_list('name', flat= True)
                workflowNames = []
                for name in names:
                    workflowNames.append(name)
                notebook["assignedWorkflow"] = workflowNames
                notebookRunLogs = NotebookRunLogs.objects.filter(notebookId=notebook["id"], workspace_id= workspaceId).order_by("-startTimestamp").first()
                if notebookRunLogs:
                    notebook["notebookStatus"] = notebookRunLogs.status if notebookRunLogs.status else None
                    notebook["lastRun"] = NotebookRunLogsSerializer(notebookRunLogs).data
            res.update(True, "NotebookObjects retrieved successfully", {"notebooks": notebooks, "count": notebookCount})
        else:
            res.update(True, "NotebookObjects retrieved successfully", [])
        return res

    @staticmethod
    def sortingOnNotebook(notebooks, sorter, _filter):
        sortedNotebookId= []
        if sorter['columnKey'] == "schedule" and sorter['order'] == 'ascend':
            sortedNotebookId = NotebookJob.objects.all().order_by("crontab__customschedule__name").values_list("notebookId", flat=True)
            for notebookId in sortedNotebookId[::-1]:
                for notebook in notebooks:
                    if notebookId == notebook["id"]:
                        toAddNotebook = notebook
                        notebooks.remove(notebook)
                        notebooks.insert(0, toAddNotebook)
        if sorter['columnKey'] == "schedule" and sorter['order'] == 'descend':
            sortedNotebookId = NotebookJob.objects.all().order_by("-crontab__customschedule__name").values_list("notebookId", flat=True)
            for notebookId in sortedNotebookId:
                for notebook in notebooks:
                    if notebookId == notebook["id"]:
                        toAddNotebook = notebook
                        notebooks.remove(notebook)
                        notebooks.append(toAddNotebook)

        if sorter['columnKey'] == 'name' and sorter['order'] == 'ascend':
            notebooks = sorted(notebooks, key = lambda notebook: notebook["path"].upper())
        
        if sorter['columnKey'] == 'name' and sorter['order'] == 'descend':
            notebooks = sorted(notebooks, key = lambda notebook: notebook["path"].upper(), reverse=True)

        if sorter['columnKey'] == "assignedWorkflow" and sorter['order'] == 'ascend':
            workflowIds = WorkflowNotebookMap.objects.all().values_list("workflow_id", flat=True)
            sortedWorkflowIds = Workflow.objects.filter(id__in = workflowIds).order_by("name").values_list("id", flat=True)
            notebookIds = WorkflowNotebookMap.objects.filter(workflow_id__in=sortedWorkflowIds).values_list("notebookId",flat=True)
            reversedNotebookIds = notebookIds[::-1]
            for notebookId in reversedNotebookIds:
                for notebook in notebooks:
                    if notebookId == notebook["id"]:
                        notebooks.remove(notebook)
                        notebooks.insert(0, notebook)

        if sorter['columnKey'] == "assignedWorkflow"and sorter['order'] == 'descend':
            workflowIds = WorkflowNotebookMap.objects.all().values_list("workflow_id", flat=True)
            sortedWorkflowIds = Workflow.objects.filter(id__in = workflowIds).order_by("name").values_list("id", flat=True)
            notebookIds = WorkflowNotebookMap.objects.filter(workflow_id__in=sortedWorkflowIds).values_list("notebookId",flat=True)
            reversedNotebookIds = notebookIds[::-1]
            for notebookId in reversedNotebookIds:
                for notebook in notebooks:
                    if notebookId == notebook["id"]:
                        notebooks.remove(notebook)
                        notebooks.append(notebook)

        if sorter['columnKey'] == "lastRun1":
            isAscending = True if sorter['order'] == "ascend" else False
            notebookIds = [notebook["id"] for notebook in notebooks]
            notebookRunLogsObjects = NotebookRunLogs.objects.filter(notebookId__in=notebookIds).order_by("notebookId", "-startTimestamp").distinct("notebookId").values("notebookId", "startTimestamp")
            sortedNotebookIds = sorted(notebookRunLogsObjects, key = lambda i: i['startTimestamp'], reverse=isAscending)
            reversedNotebookIds = sortedNotebookIds[::-1]
            for notebookId in reversedNotebookIds:
                for notebook in notebooks:
                    if notebookId["notebookId"] == notebook["id"]:
                        notebooks.remove(notebook)
                        notebooks.insert(0,notebook)

        if _filter.get('lastRun2' , None) != None:
            if "lastRun2" in _filter:
                # import pdb; pdb.set_trace();
                notebookIds = [notebook["id"] for notebook in notebooks]
                notebookRunLogsObjects = NotebookRunLogs.objects.filter(notebookId__in=notebookIds).order_by("notebookId", "-startTimestamp").distinct("notebookId").values("notebookId", "status")
                filteredNotebookIds = [notebookRunLogsObject["notebookId"] for notebookRunLogsObject in notebookRunLogsObjects if notebookRunLogsObject['status'] in _filter['lastRun2']]
                notebooks = [notebook for notebook in notebooks if notebook["id"] in filteredNotebookIds]

        return notebooks

    @staticmethod
    def archivedNotebooks(workspaceId: int = 0):
        """
        Get archived notebooks
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error retrieving archived notebooks")
        notebooks =  ZeppelinAPI(workspaceName).getAllNotebooks("~Trash")
        if notebooks:
            res.update(True, "Archived notebooks retrieved successfully", notebooks)
        return res

    @staticmethod
    def getNotebookObject(notebookObjId: int):
        """
        Service to fetch specified NotebookObject
        :param notebookObjId: ID of the notebook object
        """
        res = ApiResponse(message="Error retrieving specified Notebook Object")
        notebookObj = NotebookObject.objects.get(id=notebookObjId)
        data = NotebookObjectSerializer(notebookObj).data
        res.update(True, "NotebookObject retrieved successfully", data)
        return res


    @staticmethod
    def getNotebooksLight(workspaceId: int = 0):
        """ Gets concise notebook data"""
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error retrieving notebooks")
        notebooks = ZeppelinAPI(workspaceName).getAllNotebooks()
        res.update(True, "Notebooks retrieved successfully", notebooks)
        return res
    
    @staticmethod
    def _prepareNotebookJson(notebookTemplate: NotebookTemplate, payload: dict):
        """
        Utility function for preparing notebook json to be sent to zeppelin
        Can be used to add a notebook or edit one
        Returns tuple containing notebook json and notebook connection
        :param notebookTemplate: NotebookTemplate object on which to base notebook
        :param payload: Dict containing notebook template variables
        """
        if "datasetLocation" in payload:
            payload["datasetLocation"] = json.loads(payload["datasetLocation"])
        context = payload # Storing payload in context variable so that it can be used for rendering
        connection = None
        # Handling connection variables
        if payload.get("sourceConnection", False):
            connection = Connection.objects.get(id=payload["sourceConnection"])
            context["sourceConnection_type"] = connection.connectionType.name
            connectionParams = connection.cpvc.all()
            for cp in connectionParams:
                paramName = cp.connectionParam.name
                context["sourceConnection_" + paramName] = cp.value
        if payload.get("targetConnection", False):
            connection = Connection.objects.get(id=payload["sourceConnection"])
            context["targetConnection_type"] = connection.connectionType.name
            connectionParams = connection.cpvc.all()
            for cp in connectionParams:
                paramName = cp.connectionParam.name
                context["targetConnection" + paramName] = cp.value
        # Handling S3 path - Splitting it to get the table name
        if payload.get("destinationTableS3Path", False):
            destinationTableName = payload["destinationTableS3Path"].rsplit('/', 1)[1]
            warehouseLocation = payload["destinationTableS3Path"].rsplit('/', 1)[0]
            context["destinationTableName"] = destinationTableName
            context["warehouseLocation"] = warehouseLocation
        # Adding a temp table name to the context
        context["tempTableName"] = "tempTable_" + str(round(time.time() * 1000))
        # Adding Druid Ingestion URL to the context
        context["druidLocation"] = "http://cueapp-druid-router:8888/druid/indexer/v1/task"
        # Adding S3 files directory in template
        context["s3FilesDirectory"] = "s3a://" + settings.S3_BUCKET_NAME + "/" + settings.S3_FILES_PREFIX 
        notebook = Template(json.dumps(notebookTemplate.template)).render(Context(context))
        return notebook, connection


    @staticmethod
    def addNotebook(payload: dict, workspaceId: int = 0):
        """
        Service to create and add a template based notebook
        :param payload: Dict containing notebook template info
        """
        res = ApiResponse(message="Error adding notebook")
        defaultPayload = payload.copy()
        notebookTemplate = NotebookTemplate.objects.get(id=payload.get("notebookTemplateId", 0))
        notebook, connection = NotebookJobServices._prepareNotebookJson(notebookTemplate, payload)
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        notebookZeppelinId = ZeppelinAPI(workspaceName).addNotebook(notebook)
        if notebookZeppelinId:
            NotebookObject.objects.create(notebookZeppelinId=notebookZeppelinId, connection=connection, notebookTemplate=notebookTemplate, defaultPayload=defaultPayload)
            res.update(True, "Notebook added successfully")
        return res

    @staticmethod
    def editNotebook(notebookObjId: int, payload: dict, workspaceId: int = 0):
        """
        Service to update a template based notebook
        :param notebookObjId: ID of the NotebookObject to be edited
        :param payload: Dict containing notebook template info
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error updating notebook")
        defaultPayload = payload.copy()
        notebookObject = NotebookObject.objects.get(id=notebookObjId)
        notebook, connection = NotebookJobServices._prepareNotebookJson(notebookObject.notebookTemplate, payload)

        updateSuccess = ZeppelinAPI(workspaceName).updateNotebookParagraphs(notebookObject.notebookZeppelinId, notebook)
        if updateSuccess:
            if defaultPayload.get("name"):
                ZeppelinAPI(workspaceName).renameNotebook(notebookObject.notebookZeppelinId, defaultPayload.get("name"))
            notebookObject.defaultPayload = defaultPayload
            notebookObject.connection = connection
            notebookObject.save()
            res.update(True, "Notebook updated successfully")
        return res
    
    @staticmethod
    def getNotebookJobDetails(notebookId: int, notebookRunLogsOffset: int = 0):
        """
        Service to fetch run details and logs of the selected NotebookJob
        :param notebookId: ID of the NotebookJob
        :param notebookRunLogsOffset: Offset for fetching NotebookJob run statuses
        """
        res = ApiResponse()
        notebookJobData = {}
        notebookRunLogs = NotebookRunLogs.objects.filter(notebookId=notebookId).order_by("-startTimestamp")[notebookRunLogsOffset: notebookRunLogsOffset + RUN_STATUS_LIMIT]
        notebookRunCount = NotebookRunLogs.objects.filter(notebookId=notebookId).count()
        notebookJobData["notebookRunLogs"] = NotebookRunLogsSerializer(notebookRunLogs, many=True).data
        notebookJobData["count"] = notebookRunCount
        res.update(True, "NotebookJobs retrieved successfully", notebookJobData)
        return res

    @staticmethod
    def addNotebookJob(notebookId: str, workspaceId: int, scheduleId: int):
        """
        Service to add a new NotebookJob
        :param notebookId: ID of the notebook for which to create job
        :param scheduleId: ID of schedule
        """
        res = ApiResponse()
        scheduleObj = Schedule.objects.get(crontabschedule_ptr_id=scheduleId)
        NotebookJob.objects.update_or_create(name=notebookId, workspace_id=workspaceId, notebookId=notebookId, defaults={"crontab":scheduleObj, "task":CELERY_TASK_NAME, "args":f'["{notebookId}", {workspaceId}]'})
        res.update(True, "NotebookJob added successfully", None)
        return res

    @staticmethod
    def deleteNotebookJob(notebookId: int, workspaceId: int):
        """
        Service to update crontab of an existing NotebookJob
        :param notebookId: ID of the Notebook for which to delete
        """
        res = ApiResponse()
        NotebookJob.objects.filter(name=notebookId, workspace_id=workspaceId).delete()
        res.update(True, "NotebookJob deleted successfully", None)
        return res

    @staticmethod
    def runNotebookJob(notebookId: str, workspaceId: int = 0):
        """
        Service to run notebook job
        """
        res = ApiResponse("Error in running notebook")
        notebookRunLogs = NotebookRunLogs.objects.create(notebookId=notebookId, workspace_id = workspaceId, status=NOTEBOOK_STATUS_QUEUED, runType="Manual")
        runNotebookJobTask.delay(notebookId=notebookId, notebookRunLogsId=notebookRunLogs.id, runType="Manual", workspaceId=workspaceId)
        res.update(True, "Notebook triggered successfully", None)
        return res

    @staticmethod
    def stopNotebookJob(notebookId: str, workspaceId: int):
        """
        Service to stop notebook job
        """
        res = ApiResponse(message="Error in stopping notebook")
        # Updating NotebookRunLogs that the task is being aborted
        notebookNotebookRunLogs = NotebookRunLogs.objects.filter(notebookId=notebookId, workspace_id=workspaceId).order_by("-startTimestamp").first()
        if(notebookNotebookRunLogs.status == NOTEBOOK_STATUS_RUNNING):
            notebookNotebookRunLogs.status = NOTEBOOK_STATUS_ABORT
            notebookNotebookRunLogs.save()
        zeppelin = ZeppelinAPI(notebookNotebookRunLogs.zeppelinServerId)
        thread = threading.Thread(target=zeppelin.stopNotebookJob, args=[notebookId])
        thread.start()
        res.update(True, "Aborting notebook job", None)
        return res

    @staticmethod
    def clearNotebookResults(notebookId: str, workspaceId: int = 0):
        """
        Service to clear notebook job
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error in clearing notebook")
        response = ZeppelinAPI(workspaceName).clearNotebookResults(notebookId)
        if response:
            res.update(True, "Notebook cleared successfully", None)
        return res

    @staticmethod
    def cloneNotebook(notebookId: str, payload: dict, workspaceId: int = 0):
        """
        Service to clone notebook job
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error in cloning notebook")
        response = ZeppelinAPI(workspaceName).cloneNotebook(notebookId, json.dumps(payload))
        if response:
            res.update(True, "Notebook cloned successfully", None)
        return res

    @staticmethod
    def archiveNotebook(notebookId: str, notebookName: str, workspaceId: int = 0):
        """ 
        Service to run notebook 
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error in archiving notebook")
        response = ZeppelinAPI(workspaceName).renameNotebook(notebookId, "~Trash/" + notebookName)
        if response:
            res.update(True, "Notebook archived successfully", None)
        return res

    @staticmethod
    def unarchiveNotebook(notebookId: str, notebookName: str, workspaceId: int = 0):
        """
        Service to unarchive notebook 
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error in archiving notebook")
        response = ZeppelinAPI(workspaceName).renameNotebook(notebookId, notebookName)
        if response:
            res.update(True, "Notebook unarchived successfully", None)
        return res

    @staticmethod
    def deleteNotebook(notebookId: str, workspaceId: int = 0):
        """
        Service to run notebook job
        """
        workspaceName = helperFunctions.getWorkspaceName(workspaceId)
        res = ApiResponse(message="Error in deleting notebook")
        response = ZeppelinAPI(workspaceName).deleteNotebook(notebookId)
        if response:
            NotebookObject.objects.filter(notebookZeppelinId=notebookId).delete()
            res.update(True, "Notebook deleted successfully", None)
        return res

    @staticmethod
    def search(notebooks, keys, text):
        """ utitlites function for search """
        filterNotebooks = []
        for notebook in notebooks:
            if text.lower() in notebook["path"].lower():
                filterNotebooks.append(notebook)

        return filterNotebooks

