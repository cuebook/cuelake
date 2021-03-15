from django_celery_beat.models import CrontabSchedule
from genie.models import NotebookJob
from genie.serializers import NotebookJobSerializer
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import ZeppelinAPI

# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob" 

class NotebookJobServices:
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
        notebooks = ZeppelinAPI().getAllNotebooks()
        notebookJobsData = NotebookJobSerializer(notebookJobs, many=True).data
        res.update(True, "NotebookJobs retrieved successfully", notebooks)
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
        NotebookJob.objects.create(name=notebookId, notebookId=notebookId, crontab=crontabScheduleObj, task=CELERY_TASK_NAME, args=f'["{notebookId}"]')
        res.update(True, "NotebookJob added successfully", None)
        return res