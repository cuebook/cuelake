from genie.models import NotebookJob
from genie.serializers import NotebookJobSerializer
from utils.apiResponse import ApiResponse

class NotebookJobServices():
    """
    Class containing services related to NotebookJob model
    """
    @staticmethod
    def getNotebookJobs():
        """
        Service to fetch and serialize all NotebookJob objects
        """
        res = ApiResponse()
        notebookJobs = NotebookJob.objects.all()
        notebookJobsData = NotebookJobSerializer(notebookJobs, many=True).data
        res.update(True, "NotebookJobs retrieved successfully", notebookJobsData)
        return res