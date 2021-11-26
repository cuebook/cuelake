from django.http import HttpRequest
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from genie.services import NotebookJobServices, Connections, NotebookTemplateService, KubernetesServices, Metastore, ScheduleService
from rest_framework.decorators import api_view

class NotebookOperationsView(APIView):
    """
    Class to get notebooks from zeppelin server
    """
    def post(self, request, notebookId):
        res = NotebookJobServices.cloneNotebook(notebookId, request.data)
        return Response(res.json())

    def delete(self, request, notebookId):
        res = NotebookJobServices.deleteNotebook(notebookId)
        return Response(res.json())

class ArchivedNotebooksView(APIView):
    """
    Class to get archived notebooks
    """
    def get(self, request):
        res = NotebookJobServices.archivedNotebooks()
        return Response(res.json())

class NotebookActionsView(APIView):
    """
    Class to get notebooks from zeppelin server
    """
    def post(self, request, notebookId):
        res = NotebookJobServices.runNotebookJob(notebookId)
        return Response(res.json())

    def delete(self, request, notebookId):
        res = NotebookJobServices.stopNotebookJob(notebookId)
        return Response(res.json())

    def put(self, request, notebookId):
        res = NotebookJobServices.clearNotebookResults(notebookId)
        return Response(res.json())

class ArchiveNotebookView(APIView):
    """
    Class to archive notebook
    """
    def get(self, request, notebookId, notebookName):
        res = NotebookJobServices.archiveNotebook(notebookId, notebookName)
        return Response(res.json())
                
class UnarchiveNotebookView(APIView):
    """
    Class to unarchive notebook
    """
    def get(self, request, notebookId, notebookName):
        res = NotebookJobServices.unarchiveNotebook(notebookId, notebookName)
        return Response(res.json())
                
class NotebooksLightView(APIView):
    """
    Get concise notebook data
    """
    def get(self, request):
        res = NotebookJobServices.getNotebooksLight()
        return Response(res.json())


class NotebookView(APIView):
    """
    Class to get notebooks from zeppelin server
    """
    def get(self, request, offset: int ):
        limit = request.GET.get('limit', 25)
        searchQuery = request.GET.get('searchText', '')
        sorter = json.loads(request.GET.get('sorter', '{}'))
        _filter = json.loads(request.GET.get('filter', '{}'))
        res = NotebookJobServices.getNotebooks(offset, limit, searchQuery, sorter, _filter)
        return Response(res.json())

    def post(self, request):
        res = NotebookJobServices.addNotebook(request.data)
        return Response(res.json())


class NotebookJobView(APIView):
    """
    Class to get, add and update a NotebookJob details
    The put and post methods only require request body and not path parameters
    The get method requires the notebookJobId as the path parameter
    """
    def get(self, request, notebookId=None):
        offset = int(request.GET.get("offset", 0))
        res = NotebookJobServices.getNotebookJobDetails(notebookId=notebookId, runStatusOffset=offset)
        return Response(res.json())
    
    def post(self, request):
        notebookId = request.data["notebookId"]
        scheduleId = request.data.get("scheduleId")
        retryCount = request.data.get("retryCount", None)

        if retryCount == None:
            res = NotebookJobServices.addNotebookJob(notebookId=notebookId, scheduleId=scheduleId)
        else:
            res = NotebookJobServices.updateNotebookRetryCount(notebookId=notebookId, retryCount=retryCount)
        return Response(res.json())

    def delete(self, request, notebookId=None):
        res = NotebookJobServices.deleteNotebookJob(notebookId=notebookId)
        return Response(res.json())

class ScheduleView(APIView):
    """
    Class to get and add available crontab schedules
    """
    def get(self, request):
        res = ScheduleService.getSchedules()
        return Response(res.json())

    def post(self, request):
        name = request.data["name"]
        cron = request.data["crontab"]
        timezone = request.data["timezone"]
        res = ScheduleService.addSchedule(cron=cron, timezone=timezone, name=name)
        return Response(res.json())
    
    def put(self,request):
        id = request.data["id"]
        name = request.data["name"]
        crontab = request.data["crontab"]
        timezone = request.data["timezone"]
        res = ScheduleService.updateSchedule(id=id, crontab=crontab, timezone=timezone, name=name)
        return Response(res.json())

@api_view(["GET", "PUT", "DELETE"])
def schedule(request: HttpRequest, scheduleId: int) -> Response:
    """
    Method for crud operations on a single connection
    :param request: HttpRequest
    :param connection_id: Connection Id
    """
    if request.method == "GET":
        res = ScheduleService.getSingleSchedule(scheduleId)
        return Response(res.json())
    if request.method == "DELETE":
        res = ScheduleService.deleteSchedule(scheduleId)
        return Response(res.json())


class TimzoneView(APIView):
    """
    Class to get standard pytz timezones
    """
    def get(self, request):
        res = ScheduleService.getTimezones()
        return Response(res.json())


# TODO 
# Change connection views to class
@api_view(["GET", "POST"])
def connections(request: HttpRequest) -> Response:
    """
    Method to get or add connection
    :param request: HttpRequest
    """
    if request.method == "GET":
        res = Connections.getConnections()
        return Response(res.json())
    elif request.method == "POST":
        res = Connections.addConnection(request.data)
        return Response(res.json())


@api_view(["GET", "PUT", "DELETE"])
def connection(request: HttpRequest, connectionId: int) -> Response:
    """
    Method for crud operations on a single connection
    :param request: HttpRequest
    :param connectionId: Connection Id
    """
    if request.method == "GET":
        res = Connections.getConnection(connectionId)
        return Response(res.json())
    elif request.method == "DELETE":
        res = Connections.removeConnection(connectionId)
        return Response(res.json())
    elif request.method == "PUT":
        res = Connections.updateConnection(connectionId, request.data)
        return Response(res.json())


@api_view(["GET", "POST"])
def connectionTypes(request: HttpRequest) -> Response:
    """
    Method to get all connection types
    :param request: HttpRequest
    """
    if request.method == "GET":
        res = Connections.getConnectionTypes()
        return Response(res.json())


@api_view(["POST"])
def datasetDetails(request: HttpRequest) -> Response:
    """
    Method to get dataset details from s3 location
    :param request: HttpRequest
    """
    datasetLocation = request.data.get("datasetLocation")
    res = NotebookTemplateService.getDatasetDetails(datasetLocation)
    return Response(res.json())

@api_view(["GET", "PUT"])
def getNotebookObject(request: HttpRequest, notebookObjId: int) -> Response:
    """
    Method to get details of Notebook Object with given id
    :param notebookObjId: ID of the notebook object
    """
    if request.method == "GET":
        res = NotebookJobServices.getNotebookObject(notebookObjId)
        return Response(res.json())
    if request.method == "PUT":
        res = NotebookJobServices.editNotebook(notebookObjId, request.data)
        return Response(res.json())


class NotebookTemplateView(APIView):
    def get(self, request):
        res = NotebookTemplateService.getNotebookTemplates()
        return Response(res.json())

class DriverAndExecutorStatus(APIView):
    def get(self, request):
        """
        Method to get drivers and executors count
        """
        res = KubernetesServices.getDriversCount()
        return Response(res.json())

class MetastoreTablesView(APIView):
    def get(self, request):
        """
        Method to get metastore tables
        """
        res = Metastore().getTables()
        return Response(res.json())

class MetastoreColumnsView(APIView):
    def get(self, request, tableId: int):
        """
        Method to get columns of a metastore table
        """
        res = Metastore().getColumns(tableId)
        return Response(res.json())
