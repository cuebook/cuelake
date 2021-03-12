from genie.services import NotebookJobServices
from rest_framework.decorators import api_view
from rest_framework.response import Response

def getNotebookJobs(request):
    res = NotebookJobServices.getNotebookJobs()
    return Response(res.json())
