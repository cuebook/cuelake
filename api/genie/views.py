from genie.services import NotebookJobServices
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

@api_view(["GET"])
def getNotebooks(request, offset: int):
    res = NotebookJobServices.getNotebooks(offset)
    return Response(res.json())

class NotebookJobView(APIView):
    """
    Class to get, add and update a NotebookJob details
    The put and post methods only require request body and not path parameters
    The get method requires the notebookJobId as the path parameter
    """
    def get(self, request, notebookJobId=None, format=None):
        res = NotebookJobServices.getNotebookJobDetails(notebookJobId=notebookJobId)
        return Response(res.json())
    
    def post(self, request, format=None):
        notebookId = request.data["notebookId"]
        crontabScheduleId = request.data["crontabScheduleId"]
        res = NotebookJobServices.addNotebookJob(notebookId=notebookId, crontabScheduleId=crontabScheduleId)
        return Response(res.json())
    
    def put(self, request, format=None):
        notebookJobId = request.data["notebookJobId"]
        crontabScheduleId = request.data["crontabScheduleId"]
        res = NotebookJobServices.updateNotebookJob(notebookJobId=notebookJobId, crontabScheduleId=crontabScheduleId)
        return Response(res.json())

@api_view(["GET"])
def getSchedules(request):
    res = NotebookJobServices.getSchedules()
    return Response(res.json())
