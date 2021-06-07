import asyncio
import json
import os
import pytz
import time
import logging
import datetime as dt
import threading
from typing import List
from django.template import Template, Context
# from django_celery_beat.models import CrontabSchedule
from genie.models import NOTEBOOK_STATUS_ABORT, NOTEBOOK_STATUS_QUEUED, NOTEBOOK_STATUS_RUNNING, NOTEBOOK_STATUS_ABORTING, NotebookObject, NotebookJob, RunStatus, Connection, ConnectionType, ConnectionParam, ConnectionParamValue, NotebookTemplate, CustomSchedule as Schedule
from genie.serializers import NotebookJobSerializer, NotebookObjectSerializer, ScheduleSerializer, RunStatusSerializer, ConnectionSerializer, ConnectionDetailSerializer, ConnectionTypeSerializer, NotebookTemplateSerializer
from workflows.models import Workflow, WorkflowRun, NotebookJob as WorkflowNotebookJob
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import Zeppelin
from utils.druidSpecGenerator import DruidIngestionSpecGenerator
from genie.tasks import runNotebookJob as runNotebookJobTask
from kubernetes import config, client
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
    async def _fetchNotebookStatuses(notebooks: list):
        """
        Async method to fetch notebook status details for multiple notebooks
        Returns a dict with notebook ids as keys
        :param notebooks: List of notebook describing dicts each containing the 'id' field
        """
        notebookStatuses = {}
        for future in asyncio.as_completed([Zeppelin.getNotebookStatus(notebook["id"]) for notebook in notebooks]):
            status = await future
            notebookStatuses[status["id"]] = status
        return notebookStatuses

    @staticmethod
    def getNotebooks(offset: int = 0, limit: int = None , searchQuery: str = None, sortColumn: str = None, sortOrder: str = None):
        """
        Service to fetch and serialize NotebookJob objects
        Number of NotebookObjects fetched is stored as the constant GET_NOTEBOOKOJECTS_LIMIT
        :param offset: Offset for fetching NotebookJob objects
        """
        res = ApiResponse(message="Error retrieving notebooks")
        notebooks = Zeppelin.getAllNotebooks()
        if searchQuery:
            notebooks = NotebookJobServices.search(notebooks, "path", searchQuery)
        if sortColumn:
            notebooks = NotebookJobServices.sortingOnNotebook(notebooks, sortColumn, sortOrder)
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
            
                assignedWorkflowId = WorkflowNotebookJob.objects.filter(notebookId = notebook["id"]).values_list("workflow_id", flat=True)
                names= Workflow.objects.filter(id__in = assignedWorkflowId).values_list('name', flat= True)
                workflowNames = []
                for name in names:
                    workflowNames.append(name)
                notebook["assignedWorkflow"] = workflowNames
                notebookRunStatus = RunStatus.objects.filter(notebookId=notebook["id"]).order_by("-startTimestamp").first()
                if notebookRunStatus:
                    notebook["notebookStatus"] = notebookRunStatus.status if notebookRunStatus.status else None
                    notebook["lastRun"] = RunStatusSerializer(notebookRunStatus).data
            res.update(True, "NotebookObjects retrieved successfully", {"notebooks": notebooks, "count": notebookCount})
        else:
            res.update(True, "NotebookObjects retrieved successfully", [])
        return res

    @staticmethod
    def sortingOnNotebook(notebooks, sortColumn, sortOrder):
        sortedNotebookId= []
        if sortColumn == "schedule" and sortOrder == 'ascend':
            sortedNotebookId = NotebookJob.objects.all().order_by("crontab__customschedule__name").values_list("notebookId", flat=True)
            for notebookId in sortedNotebookId[::-1]:
                for notebook in notebooks:
                    if notebookId == notebook["id"]:
                        toAddNotebook = notebook
                        notebooks.remove(notebook)
                        notebooks.insert(0, toAddNotebook)
        if sortColumn == "schedule" and sortOrder == 'descend':
            sortedNotebookId = NotebookJob.objects.all().order_by("-crontab__customschedule__name").values_list("notebookId", flat=True)
            for notebookId in sortedNotebookId:
                for notebook in notebooks:
                    if notebookId == notebook["id"]:
                        toAddNotebook = notebook
                        notebooks.remove(notebook)
                        notebooks.append(toAddNotebook)

        if sortColumn == 'name' and sortOrder == 'ascend':
            notebooks = sorted(notebooks, key = lambda notebook: notebook["path"].upper())
        
        if sortColumn == 'name' and sortOrder == 'descend':
            notebooks = sorted(notebooks, key = lambda notebook: notebook["path"].upper(), reverse=True)

        if sortColumn == "assignedWorkflow" and sortOrder == 'ascend':
            workflowIds = WorkflowNotebookJob.objects.all().values_list("workflow_id", flat=True)
            sortedWorkflowIds = Workflow.objects.filter(id__in = workflowIds).order_by("name").values_list("id", flat=True)
            notebookIds = WorkflowNotebookJob.objects.filter(workflow_id__in=sortedWorkflowIds).values_list("notebookId",flat=True)
            reversedNotebookIds = notebookIds[::-1]
            for notebookId in reversedNotebookIds:
                for notebook in notebooks:
                    if notebookId == notebook["id"]:
                        notebooks.remove(notebook)
                        notebooks.insert(0, notebook)

        if sortColumn == "assignedWorkflow"and sortOrder == 'descend':
            workflowIds = WorkflowNotebookJob.objects.all().values_list("workflow_id", flat=True)
            sortedWorkflowIds = Workflow.objects.filter(id__in = workflowIds).order_by("name").values_list("id", flat=True)
            notebookIds = WorkflowNotebookJob.objects.filter(workflow_id__in=sortedWorkflowIds).values_list("notebookId",flat=True)
            reversedNotebookIds = notebookIds[::-1]
            for notebookId in reversedNotebookIds:
                for notebook in notebooks:
                    if notebookId == notebook["id"]:
                        notebooks.remove(notebook)
                        notebooks.append(notebook)

        if sortColumn == "lastRun1":
            isAscending = True if sortOrder == "ascend" else False
            notebookIds = [notebook["id"] for notebook in notebooks]
            runStatusObjects = RunStatus.objects.filter(notebookId__in=notebookIds).order_by("notebookId", "-startTimestamp").distinct("notebookId").values("notebookId", "startTimestamp")
            sortedNotebookIds = sorted(runStatusObjects, key = lambda i: i['startTimestamp'], reverse=isAscending)
            reversedNotebookIds = sortedNotebookIds[::-1]
            for notebookId in reversedNotebookIds:
                for notebook in notebooks:
                    if notebookId["notebookId"] == notebook["id"]:
                        notebooks.remove(notebook)
                        notebooks.insert(0,notebook)
        
        if sortColumn == "lastRun2":
            isAscending = True if sortOrder == "ascend" else False
            notebookIds = [notebook["id"] for notebook in notebooks]
            runStatusObjects = RunStatus.objects.filter(notebookId__in=notebookIds).order_by("notebookId", "-startTimestamp").distinct("notebookId").values("notebookId", "status")
            sortedNotebookIds = sorted(runStatusObjects, key = lambda i: i['status'], reverse=isAscending)
            reversedNotebookIds = sortedNotebookIds[::-1]
            for notebookid in reversedNotebookIds:
                for notebook in notebooks:
                    if notebookid["notebookId"] == notebook["id"]:
                        notebooks.remove(notebook)
                        notebooks.insert(0,notebook)

        return notebooks

    @staticmethod
    def archivedNotebooks():
        """
        Get archived notebooks
        """
        res = ApiResponse(message="Error retrieving archived notebooks")
        notebooks = Zeppelin.getAllNotebooks("~Trash")
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
    def getNotebooksLight():
        """ Gets concise notebook data"""
        res = ApiResponse(message="Error retrieving notebooks")
        notebooks = Zeppelin.getAllNotebooks()
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
    def addNotebook(payload: dict):
        """
        Service to create and add a template based notebook
        :param payload: Dict containing notebook template info
        """
        res = ApiResponse(message="Error adding notebook")
        defaultPayload = payload.copy()
        notebookTemplate = NotebookTemplate.objects.get(id=payload.get("notebookTemplateId", 0))
        notebook, connection = NotebookJobServices._prepareNotebookJson(notebookTemplate, payload)
        notebookZeppelinId = Zeppelin.addNotebook(notebook)
        if notebookZeppelinId:
            NotebookObject.objects.create(notebookZeppelinId=notebookZeppelinId, connection=connection, notebookTemplate=notebookTemplate, defaultPayload=defaultPayload)
            res.update(True, "Notebook added successfully")
        return res

    @staticmethod
    def editNotebook(notebookObjId: int, payload: dict):
        """
        Service to update a template based notebook
        :param notebookObjId: ID of the NotebookObject to be edited
        :param payload: Dict containing notebook template info
        """
        res = ApiResponse(message="Error updating notebook")
        defaultPayload = payload.copy()
        notebookObject = NotebookObject.objects.get(id=notebookObjId)
        notebook, connection = NotebookJobServices._prepareNotebookJson(notebookObject.notebookTemplate, payload)

        updateSuccess = Zeppelin.updateNotebookParagraphs(notebookObject.notebookZeppelinId, notebook)
        if updateSuccess:
            print(defaultPayload)
            if defaultPayload.get("name"):
                Zeppelin.renameNotebook(notebookObject.notebookZeppelinId, defaultPayload.get("name"))
            notebookObject.defaultPayload = defaultPayload
            notebookObject.connection = connection
            notebookObject.save()
            res.update(True, "Notebook updated successfully")
        return res
    
    @staticmethod
    def getNotebookJobDetails(notebookId: int, runStatusOffset: int = 0):
        """
        Service to fetch run details and logs of the selected NotebookJob
        :param notebookId: ID of the NotebookJob
        :param runStatusOffset: Offset for fetching NotebookJob run statuses
        """
        res = ApiResponse()
        notebookJobData = {}
        runStatuses = RunStatus.objects.filter(notebookId=notebookId).order_by("-startTimestamp")[runStatusOffset: runStatusOffset + RUN_STATUS_LIMIT]
        notebookRunCount = RunStatus.objects.filter(notebookId=notebookId).count()
        notebookJobData["runStatuses"] = RunStatusSerializer(runStatuses, many=True).data
        notebookJobData["count"] = notebookRunCount
        res.update(True, "NotebookJobs retrieved successfully", notebookJobData)
        return res

    @staticmethod
    def addNotebookJob(notebookId: str, scheduleId: int):
        """
        Service to add a new NotebookJob
        :param notebookId: ID of the notebook for which to create job
        :param scheduleId: ID of schedule
        """
        res = ApiResponse()
        scheduleObj = Schedule.objects.get(crontabschedule_ptr_id=scheduleId)
        NotebookJob.objects.update_or_create(name=notebookId, notebookId=notebookId, defaults={"crontab":scheduleObj, "task":CELERY_TASK_NAME, "args":f'["{notebookId}"]'})
        res.update(True, "NotebookJob added successfully", None)
        return res

    @staticmethod
    def updateNotebookJob(notebookJobId: int, scheduleId: int):
        """
        Service to update crontab of an existing NotebookJob
        :param notebookId: ID of the NotebookJob for which to update crontab
        :param scheduleId: ID of schedule
        """
        res = ApiResponse()
        scheduleObj = Schedule.objects.get(crontabschedule_ptr_id=scheduleId)
        NotebookJob.objects.filter(id=notebookJobId).update(crontab=scheduleObj)
        res.update(True, "NotebookJob updated successfully", None)
        return res

    @staticmethod
    def deleteNotebookJob(notebookId: int):
        """
        Service to update crontab of an existing NotebookJob
        :param notebookId: ID of the Notebook for which to delete
        """
        res = ApiResponse()
        NotebookJob.objects.filter(name=notebookId).delete()
        res.update(True, "NotebookJob deleted successfully", None)
        return res

    @staticmethod
    def toggleNotebookJob(notebookId: int, enabled: bool):
        """
        Service to update crontab of an existing NotebookJob
        :param notebookId: ID of the NotebookJob for which to update crontab
        :param scheduleId: ID of schedule
        """
        res = ApiResponse()
        NotebookJob.objects.filter(notebookId=notebookId).update(enabled=enabled)
        res.update(True, "NotebookJob updated successfully", None)
        return res

    @staticmethod
    def getSchedules():
        """
        Service to get all schedule objects
        """
        res = ApiResponse()
        schedules = Schedule.objects.exclude(id=1)
        data = ScheduleSerializer(schedules, many=True).data
        res.update(True, "Schedules fetched successfully", data)
        return res
    
    @staticmethod
    def addSchedule(cron: str, timezone: str = None, name: str = ""):
        """
        Service to add Schedule
        :param cron: Crontab in string format
        :param timezone: Timezone string for which to configure Schedule
        :param name: Name of schedule provided by user
        """
        res = ApiResponse()
        cronElements = cron.split()
        if len(cronElements) != 5:
            res.update(False, "Crontab must contain five elements")
            return res        
        timezone = timezone if timezone else "UTC"
        schedule = Schedule.objects.create(
            minute=cronElements[0],
            hour=cronElements[1],
            day_of_month=cronElements[2],
            month_of_year=cronElements[3],
            day_of_week=cronElements[4],
            timezone=timezone,
            name=name,
        )
        res.update(True, "Schedule added successfully", schedule.id)
        return res
        
    @staticmethod
    def getSingleSchedule(scheduleId: int):
        """
        Service to get singleSchedule
        :param scheduleId: int
        """

        res = ApiResponse()
        schedules = Schedule.objects.filter(crontabschedule_ptr_id=scheduleId)
        data = ScheduleSerializer(schedules, many=True).data
        res.update(True, "Schedules fetched successfully", data)
        return res

    @staticmethod
    def updateSchedule(id, crontab, timezone, name):
        """
        Service to update Schedule
        param id: int
        param cron: Crontab in string format
        param timezone: Timezone in string format
        param name: String
        """
        res = ApiResponse()
        cronElements = crontab.split(" ")
        if len(cronElements) != 5:
            res.update(False, "Crontab must contain five elements")
            return res 
        schedule = Schedule.objects.get(crontabschedule_ptr_id=id)
        schedule.minute=cronElements[0]
        schedule.hour=cronElements[1]
        schedule.day_of_month=cronElements[2]
        schedule.month_of_year=cronElements[3]
        schedule.day_of_week=cronElements[4]
        schedule.timezone = timezone
        schedule.name = name
        schedule.save()
        res.update(True, "Schedules updated successfully", [])
        return res

    @staticmethod
    def deleteSchedule(scheduleId: int):
        """ Service to delete schedule of given scheduleId """
        res = ApiResponse()
        Schedule.objects.filter(id=scheduleId).delete()
        res.update(True, "Schedules deleted successfully", [])
        return res

    @staticmethod
    def getTimezones():
        """
        Service to fetch all pytz timezones
        """
        res = ApiResponse()
        timezones = pytz.all_timezones
        res.update(True, "Timezones fetched successfully", timezones)
        return res

    @staticmethod
    def runNotebookJob(notebookId: str):
        """
        Service to run notebook job
        """
        res = ApiResponse("Error in running notebook")
        runStatus = RunStatus.objects.create(notebookId=notebookId, status=NOTEBOOK_STATUS_QUEUED, runType="Manual")
        runNotebookJobTask.delay(notebookId=notebookId, runStatusId=runStatus.id, runType="Manual")
        res.update(True, "Notebook triggered successfully", None)
        return res

    @staticmethod
    def stopNotebookJob(notebookId: str):
        """
        Service to stop notebook job
        """
        res = ApiResponse(message="Error in stopping notebook")
        # Updating runStatus that the task is being aborted
        notebookRunStatus = RunStatus.objects.filter(notebookId=notebookId).order_by("-startTimestamp").first()
        if(notebookRunStatus.status == NOTEBOOK_STATUS_RUNNING):
            notebookRunStatus.status = NOTEBOOK_STATUS_ABORT
            notebookRunStatus.save()
        thread = threading.Thread(target=Zeppelin.stopNotebookJob, args=[notebookId])
        thread.start()
        res.update(True, "Aborting notebook job", None)
        return res

    @staticmethod
    def clearNotebookResults(notebookId: str):
        """
        Service to clear notebook job
        """
        res = ApiResponse(message="Error in clearing notebook")
        response = Zeppelin.clearNotebookResults(notebookId)
        if response:
            res.update(True, "Notebook cleared successfully", None)
        return res

    @staticmethod
    def cloneNotebook(notebookId: str, payload: dict):
        """
        Service to clone notebook job
        """
        res = ApiResponse(message="Error in cloning notebook")
        response = Zeppelin.cloneNotebook(notebookId, json.dumps(payload))
        if response:
            res.update(True, "Notebook cloned successfully", None)
        return res

    @staticmethod
    def archiveNotebook(notebookId: str, notebookName: str):
        """ 
        Service to run notebook 
        """
        res = ApiResponse(message="Error in archiving notebook")
        response = Zeppelin.renameNotebook(notebookId, "~Trash/" + notebookName)
        if response:
            res.update(True, "Notebook archived successfully", None)
        return res

    @staticmethod
    def unarchiveNotebook(notebookId: str, notebookName: str):
        """
        Service to unarchive notebook 
        """
        res = ApiResponse(message="Error in archiving notebook")
        response = Zeppelin.renameNotebook(notebookId, notebookName)
        if response:
            res.update(True, "Notebook unarchived successfully", None)
        return res

    @staticmethod
    def deleteNotebook(notebookId: str):
        """
        Service to run notebook job
        """
        res = ApiResponse(message="Error in deleting notebook")
        response = Zeppelin.deleteNotebook(notebookId)
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

class Connections:

    @staticmethod
    def getConnections():
        res = ApiResponse()
        connections = Connection.objects.all()
        serializer = ConnectionSerializer(connections, many=True)
        res.update(True, "Connections retrieved successfully", serializer.data)
        return res

    @staticmethod
    def getConnection(connection_id):
        res = ApiResponse()
        connections = Connection.objects.get(id=connection_id)
        serializer = ConnectionDetailSerializer(connections)
        res.update(True, "Connection retrieved successfully", serializer.data)
        return res

    @staticmethod
    def addConnection(payload):
        res = ApiResponse()
        connectionType = ConnectionType.objects.get(id=payload["connectionType_id"])
        connection = Connection.objects.create(
            name=payload["name"], description=payload["description"], connectionType=connectionType
        )
        for param in payload["params"]:
            cp = ConnectionParam.objects.get(name=param, connectionType=connectionType)
            ConnectionParamValue.objects.create(
                connectionParam=cp, value=payload["params"][param], connection=connection
            )
        res.update(True, "Connection added successfully")
        return res

    @staticmethod
    def removeConnection(connection_id):
        res = ApiResponse()
        connection = Connection.objects.get(id=connection_id)
        if connection.notebookobject_set.count() == 0:
            Connection.objects.get(id=connection_id).delete()
            res.update(True, "Connection deleted successfully")
        else:
            res.update(False, "Cannot delete connection because of dependent notebook")
        return res

    @staticmethod
    def updateConnection(connection_id, payload):
        res = ApiResponse()
        Connection.objects.filter(id=connection_id).update(
            name=payload.get("name", ""),
            description=payload.get("description", ""),
            connectionType=ConnectionType.objects.get(id=payload["connectionType_id"]),
        )
        connection = Connection.objects.get(id=connection_id)
        # ToDo: delete params related to this & then update
        for param in payload["params"]:
            cp = ConnectionParam.objects.get(id=param["paramId"])
            # if cp.isEncrypted:
            #     encryptionObject= AESCipher()
            #     param['paramValue'] = encryptionObject.encrypt(param['paramValue'])
            ConnectionParamValue.objects.create(
                connectionParam=cp, value=param["paramValue"], connection=connection
            )

        res.update(True, "Connection updated successfully")
        return res

    @staticmethod
    def getConnectionTypes():
        res = ApiResponse()
        connectionTypes = ConnectionType.objects.all()
        serializer = ConnectionTypeSerializer(connectionTypes, many=True)
        res.update(True, "Successfully retrieved connection types", serializer.data)
        return res


class NotebookTemplateService:

    @staticmethod
    def getNotebookTemplates():
        res = ApiResponse()
        templates = NotebookTemplate.objects.all()
        serializer = NotebookTemplateSerializer(templates, many=True)
        res.update(True, "Connections retrieved successfully", serializer.data)
        return res
    
    @staticmethod
    def getDatasetDetails(datasetLocation):
        """
        Service to fetch S3 dataset details
        :param datasetLocation: Location of the S3 bucket
        """
        res = ApiResponse()
        schema = DruidIngestionSpecGenerator._getSchemaForDatasourceInS3(datasetLocation)
        ingestionSpec = DruidIngestionSpecGenerator.getIngestionSpec(
            datasetLocation=datasetLocation, datasetSchema=schema
        )
        s3DatasetSchema = list(map(lambda x: {"columnName": x.name, "dataType": "TIMESTAMP" if x.physical_type == "INT96" else x.logical_type.type}, schema))
        datasetDetails = {
            "dremioSchema": s3DatasetSchema,
            "druidIngestionSpec": ingestionSpec
        } 
        res.update(True, "Dataset schema retrieved successfully", datasetDetails)
        return res

class KubernetesServices:

    @staticmethod
    def getDriversCount():
        """
        Gets Driver and executors count
        """
        res = ApiResponse()
        if os.environ.get("POSTGRES_DB_HOST","") == "localhost":
            config.load_kube_config()
        else:
            config.load_incluster_config()
        runningDrivers = 0
        runningExecutors = 0
        pendingDrivers = 0
        pendingExecutors = 0
        v1 = client.CoreV1Api()
        POD_NAMESPACE = os.environ.get("POD_NAMESPACE","cuelake")
        ret = v1.list_namespaced_pod(POD_NAMESPACE, watch=False)
        pods = ret.items
        pods_name = [pod.metadata.name for pod in pods]
        podLabels = [[pod.metadata.labels, pod.status.phase] for pod in pods] # list
        podStatus = [pod.status for pod in pods]

        for label in podLabels:
            if "interpreterSettingName" in label[0] and label[0]["interpreterSettingName"] == "spark" and label[1]=="Running":
                runningDrivers += 1
            
            if "interpreterSettingName" in label[0] and label[0]["interpreterSettingName"] == "spark" and label[1]=="Pending":
                pendingDrivers += 1
            if "spark-role" in label[0] and label[0]["spark-role"] == "executor" and label[1]=="Running":
                runningExecutors += 1
            
            if "spark-role" in label[0] and label[0]["spark-role"] == "executor" and label[1]=="Pending":
                pendingExecutors += 1
        data = {"runningDrivers":runningDrivers,
                "pendingDrivers":pendingDrivers,
                "runningExecutors":runningExecutors,
                "pendingExecutors":pendingExecutors
                }
        res.update(True, "Pods status retrieved successfully", data)
        return res
