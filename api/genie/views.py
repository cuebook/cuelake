from genie.services import NotebookJobServices
from rest_framework.views import APIView
from rest_framework.response import Response

class NotebookView(APIView):
    """
    Class to get notebooks from zeppelin server
    """
    def get(self, request, offset: int):
        res = NotebookJobServices.getNotebooks(offset)
        return Response(res.json())

class NotebookJobView(APIView):
    """
    Class to get, add and update a NotebookJob details
    The put and post methods only require request body and not path parameters
    The get method requires the notebookJobId as the path parameter
    """
    def get(self, request, notebookJobId=None):
        res = NotebookJobServices.getNotebookJobDetails(notebookJobId=notebookJobId)
        return Response(res.json())
    
    def post(self, request):
        notebookId = request.data["notebookId"]
        crontabScheduleId = request.data["crontabScheduleId"]
        res = NotebookJobServices.addNotebookJob(notebookId=notebookId, crontabScheduleId=crontabScheduleId)
        return Response(res.json())
    
    def put(self, request):
        notebookJobId = request.data["notebookJobId"]
        crontabScheduleId = request.data["crontabScheduleId"]
        res = NotebookJobServices.updateNotebookJob(notebookJobId=notebookJobId, crontabScheduleId=crontabScheduleId)
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

