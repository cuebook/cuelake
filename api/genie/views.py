from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from genie.services import NotebookJobServices, Connections, NotebookTemplateService
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

        
class NotebooksLight(APIView):
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
    def get(self, request, offset: int):
        res = NotebookJobServices.getNotebooks(offset)
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
        crontabScheduleId = request.data["crontabScheduleId"]
        res = NotebookJobServices.addNotebookJob(notebookId=notebookId, crontabScheduleId=crontabScheduleId)
        return Response(res.json())
    
    def put(self, request):
        notebookId = request.data["notebookId"]
        if "crontabScheduleId" in request.data:
            crontabScheduleId = request.data["crontabScheduleId"]
            res = NotebookJobServices.updateNotebookJob(notebookId=notebookId, crontabScheduleId=crontabScheduleId)
        elif "enabled" in request.data:
            enabled = request.data["enabled"]
            res = NotebookJobServices.toggleNotebookJob(notebookId=notebookId, enabled=enabled)
        return Response(res.json())

    def delete(self, request, notebookId=None):
        res = NotebookJobServices.deleteNotebookJob(notebookId=notebookId)
        return Response(res.json())

class ScheduleView(APIView):
    """
    Class to get and add available crontab schedules
    """
    def get(self, request):
        res = NotebookJobServices.getSchedules()
        return Response(res.json())

    def post(self, request):
        name = request.data["name"]
        cron = request.data["crontab"]
        timezone = request.data["timezone"]
        res = NotebookJobServices.addSchedule(cron=cron, timezone=timezone, name=name)
        return Response(res.json())
    
    def put(self,request):
        id = request.data["id"]
        name = request.data["name"]
        cron = request.data["crontab"]
        timezone = request.data["timezone"]
        res = NotebookJobServices.updateSchedule(id=id, cron=cron, timezone=timezone, name=name)
        return Response(res.json())

@api_view(["GET", "PUT", "DELETE"])
def schedule(request: HttpRequest, scheduleId: int) -> Response:
    """
    Method for crud operations on a single connection
    :param request: HttpRequest
    :param connection_id: Connection Id
    """
    if request.method == "GET":
        res = NotebookJobServices.getSingleSchedule(scheduleId)
        return Response(res.json())
    if request.method == "DELETE":
        res = NotebookJobServices.deleteSchedule(scheduleId)
        return Response(res.json())
class TimzoneView(APIView):
    """
    Class to get standard pytz timezones
    """
    def get(self, request):
        res = NotebookJobServices.getTimezones()
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
def connection(request: HttpRequest, connection_id: int) -> Response:
    """
    Method for crud operations on a single connection
    :param request: HttpRequest
    :param connection_id: Connection Id
    """
    if request.method == "GET":
        res = Connections.getConnection(connection_id)
        return Response(res.json())
    elif request.method == "DELETE":
        res = Connections.removeConnection(connection_id)
        return Response(res.json())
    elif request.method == "PUT":
        res = Connections.updateConnection(connection_id, request.data)
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



class NotebookTemplateView(APIView):
    def get(self, request):
        res = NotebookTemplateService.getNotebookTemplates()
        return Response(res.json())