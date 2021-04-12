from rest_framework.views import APIView
from rest_framework.response import Response
from genie.services import NotebookJobServices

class NotebookView(APIView):
    """
    Class to get notebooks from zeppelin server
    """
    def get(self, request, offset: int):
        res = NotebookJobServices.getNotebooks(offset)
        return Response(res.json())

    def post(self, request, notebookId):
        res = NotebookJobServices.runNotebookJob(notebookId)
        return Response(res.json())

    def delete(self, request, notebookId):
        res = NotebookJobServices.stopNotebookJob(notebookId)
        return Response(res.json())

    def put(self, request, notebookId):
        res = NotebookJobServices.clearNotebookResults(notebookId)
        return Response(res.json())

class NotebookJobView(APIView):
    """
    Class to get, add and update a NotebookJob details
    The put and post methods only require request body and not path parameters
    The get method requires the notebookJobId as the path parameter
    """
    def get(self, request, notebookJobId=None):
        offset = int(request.GET.get("offset", 0))
        res = NotebookJobServices.getNotebookJobDetails(notebookJobId=notebookJobId, runStatusOffset=offset)
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

class ScheduleView(APIView):
    """
    Class to get and add available crontab schedules
    """
    def get(self, request):
        res = NotebookJobServices.getSchedules()
        return Response(res.json())

    def post(self, request):
        cron = request.data["crontab"]
        timezone = request.data["timezone"]
        res = NotebookJobServices.addSchedule(cron=cron, timezone=timezone)
        return Response(res.json())
    
class TimzoneView(APIView):
    """
    Class to get standard pytz timezones
    """
    def get(self, request):
        res = NotebookJobServices.getTimezones()
        return Response(res.json())

