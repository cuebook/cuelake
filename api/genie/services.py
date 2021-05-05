import asyncio
import json
import pytz
import time
from django.template import Template, Context
from django_celery_beat.models import CrontabSchedule
from genie.models import NotebookJob, RunStatus, Connection, ConnectionType, ConnectionParam, ConnectionParamValue, NotebookTemplate
from genie.serializers import NotebookJobSerializer, CrontabScheduleSerializer, RunStatusSerializer, ConnectionSerializer, ConnectionDetailSerializer, ConnectionTypeSerializer, NotebookTemplateSerializer
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import Zeppelin
from utils.druidSpecGenerator import DruidIngestionSpecGenerator
from genie.tasks import runNotebookJob as runNotebookJobTask

# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"

GET_NOTEBOOKJOBS_LIMIT = 10
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
    def getNotebooks(offset: int = 0):
        """
        Service to fetch and serialize NotebookJob objects
        Number of NotebookJobs fetched is stored as the constant GET_NOTEBOOKJOBS_LIMIT
        :param offset: Offset for fetching NotebookJob objects
        """
        res = ApiResponse(message="Error retrieving notebooks")
        notebooks = Zeppelin.getAllNotebooks()
        if notebooks:
            notebookCount = len(notebooks)
            notebooks = notebooks[offset: offset + GET_NOTEBOOKJOBS_LIMIT]
            notebookIds = [notebook["id"] for notebook in notebooks]
            notebookJobs = NotebookJob.objects.filter(notebookId__in=notebookIds)
            for notebook in notebooks:
                notebook["name"] = notebook["path"]
                notebookJob = next((notebookJob for notebookJob in notebookJobs if notebookJob.name == notebook["id"]), False)
                if notebookJob:
                    notebook["isScheduled"] = True
                    notebook["schedule"] = str(notebookJob.crontab)
                    notebook["isActive"] = notebookJob.enabled
                    notebook["notebookJobId"] = notebookJob.id
                else:
                    notebook["isScheduled"] = False
                notebookRunStatus = RunStatus.objects.filter(notebookId=notebook["id"]).order_by("-startTimestamp").first()
                if notebookRunStatus:
                    notebook["lastRun"] = RunStatusSerializer(notebookRunStatus).data
            res.update(True, "NotebookJobs retrieved successfully", {"notebooks": notebooks, "count": notebookCount})
        return res

    @staticmethod
    def getNotebooksLight():
        """ Gets concise notebook data"""
        res = ApiResponse(message="Error retrieving notebooks")
        notebooks = Zeppelin.getAllNotebooks()
        res.update(True, "Notebooks retrieved successfully", notebooks)
        return res


    @staticmethod
    def addNotebook(payload):
        res = ApiResponse(message="Error adding notebook")
        notebookTemplate = NotebookTemplate.objects.get(id=payload.get("notebookTemplateId", 0))
        context = payload # Storing payload in context variable so that it can be used for rendering
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
        notebook = Template(notebookTemplate.template).render(Context(context))
        response = Zeppelin.addNotebook(notebook)
        if response:
            res.update(True, "Notebook added successfully")
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
    def addNotebookJob(notebookId: str, crontabScheduleId: int):
        """
        Service to add a new NotebookJob
        :param notebookId: ID of the notebook for which to create job
        :param crontabScheduleId: ID of CrontabSchedule
        """
        res = ApiResponse()
        crontabScheduleObj = CrontabSchedule.objects.get(id=crontabScheduleId)
        NotebookJob.objects.update_or_create(name=notebookId, notebookId=notebookId, defaults={"crontab":crontabScheduleObj, "task":CELERY_TASK_NAME, "args":f'["{notebookId}"]'})
        res.update(True, "NotebookJob added successfully", None)
        return res

    @staticmethod
    def updateNotebookJob(notebookJobId: int, crontabScheduleId: int):
        """
        Service to update crontab of an existing NotebookJob
        :param notebookId: ID of the NotebookJob for which to update crontab
        :param crontabScheduleId: ID of CrontabSchedule
        """
        res = ApiResponse()
        crontabScheduleObj = CrontabSchedule.objects.get(id=crontabScheduleId)
        NotebookJob.objects.filter(id=notebookJobId).update(crontab=crontabScheduleObj)
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
        :param crontabScheduleId: ID of CrontabSchedule
        """
        res = ApiResponse()
        NotebookJob.objects.filter(notebookId=notebookId).update(enabled=enabled)
        res.update(True, "NotebookJob updated successfully", None)
        return res

    @staticmethod
    def getSchedules():
        """
        Service to get all CrontabSchedule objects
        """
        res = ApiResponse()
        crontabSchedules = CrontabSchedule.objects.all()
        data = CrontabScheduleSerializer(crontabSchedules, many=True).data
        res.update(True, "Schedules fetched successfully", data)
        return res
    
    @staticmethod
    def addSchedule(cron: str, timezone: str = None):
        """
        Service to add CrontabSchedule
        :param cron: Crontab in string format
        :param timezone: Timezone string for which to configure CrontabSchedule
        """
        res = ApiResponse()
        cronElements = cron.split()
        if len(cronElements) != 5:
            res.update(False, "Crontab must contain five elements")
            return res        
        timezone = timezone if timezone else "UTC"
        CrontabSchedule.objects.create(
            minute=cronElements[0],
            hour=cronElements[1],
            day_of_month=cronElements[2],
            month_of_year=cronElements[3],
            day_of_week=cronElements[4],
            timezone=timezone
        )
        res.update(True, "Schedule added successfully", None)
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
        runNotebookJobTask.delay(notebookId=notebookId, runType="Manual")
        res.update(True, "Notebook triggered successfully", None)
        return res

    @staticmethod
    def stopNotebookJob(notebookId: str):
        """
        Service to run notebook job
        """
        res = ApiResponse(message="Error in stopping notebook")
        # TODO
        # Update runStatus that the task was aborted
        response = Zeppelin.stopNotebookJob(notebookId)
        if response:
            res.update(True, "Notebook stopped successfully", None)
        return res

    @staticmethod
    def clearNotebookResults(notebookId: str):
        """
        Service to run notebook job
        """
        res = ApiResponse(message="Error in clearing notebook")
        response = Zeppelin.clearNotebookResults(notebookId)
        if response:
            res.update(True, "Notebook cleared successfully", None)
        return res

    @staticmethod
    def cloneNotebook(notebookId: str, payload: dict):
        """
        Service to run notebook job
        """
        res = ApiResponse(message="Error in cloning notebook")
        response = Zeppelin.cloneNotebook(notebookId, json.dumps(payload))
        if response:
            res.update(True, "Notebook cloned successfully", None)
        return res

    @staticmethod
    def deleteNotebook(notebookId: str):
        """
        Service to run notebook job
        """
        res = ApiResponse(message="Error in cloning notebook")
        response = Zeppelin.deleteNotebook(notebookId)
        if response:
            res.update(True, "Notebook deleted successfully", None)
        return res


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
        Connection.objects.get(id=connection_id).delete()
        res.update(True, "Connection deleted successfully")
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
    def getDatasetDetails(datasetLocation, datasourceName):
        """
        Service to fetch S3 dataset details
        :param datasetLocation: Location of the S3 bucket
        """
        res = ApiResponse()
        schema = DruidIngestionSpecGenerator._getSchemaForDatasourceInS3(datasetLocation)
        ingestionSpec = DruidIngestionSpecGenerator.getIngestionSpec(
            datasetLocation=datasetLocation, datasourceName=datasourceName, datasetSchema=schema
        )
        s3DatasetSchema = list(map(lambda x: {"columnName": x.name, "dataType": x.logical_type.type}, schema))
        datasetDetails = {
            "dremioSchema": s3DatasetSchema,
            "druidIngestionSpec": ingestionSpec
        } 
        res.update(True, "Dataset schema retrieved successfully", datasetDetails)
        return res