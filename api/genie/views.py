import requests
from genie.services import NotebookJobServices
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def getNotebookJobs(request):
    res = NotebookJobServices.getNotebookJobs()
    return Response(res.json())

@api_view(["POST"])
def addNotebookJob(request):
    notebookId = request.data["notebookId"]
    crontabScheduleId = request.data["crontabScheduleId"]
    res = NotebookJobServices.addNotebookJob(notebookId=notebookId, crontabScheduleId=crontabScheduleId)
    return Response(res.json())
