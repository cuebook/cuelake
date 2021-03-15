import asyncio
from django_celery_beat.models import CrontabSchedule
from genie.models import NotebookJob
from genie.serializers import NotebookJobSerializer
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import ZeppelinAPI

# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"
GET_NOTEBOOKJOBS_LIMIT = 5

class NotebookJobServices:
    """
    Class containing services related to NotebookJob model
    """
    @staticmethod
    async def _fetchNotebookStatuses(notebooks: list):
        """
        Async method to fetch notebook status details for multiple notebooks
        :param notebooks: List of notebook describing dicts each containing the 'id' field
        """
        zeppelinApiObj = ZeppelinAPI()
        notebookStatuses = await asyncio.gather(*(zeppelinApiObj.getNotebookStatus(notebook["id"]) for notebook in notebooks))
        return notebookStatuses

    @staticmethod
    def getNotebooks(offset: int = 0):
        """
        Service to fetch and serialize NotebookJob objects
        Number of NotebookJobs fetched is stored as the constant GET_NOTEBOOKJOBS_LIMIT
        :param offset: Offset for fetching NotebookJob objects
        """
        res = ApiResponse()
        notebooks = ZeppelinAPI().getAllNotebooks()[offset: offset + GET_NOTEBOOKJOBS_LIMIT]
        notebookStatuses = asyncio.run(NotebookJobServices._fetchNotebookStatuses(notebooks))
        for i in range(len(notebookStatuses)):
            notebookStatuses[i]["name"] = notebooks[i]["path"]
            notebookJob = NotebookJob.objects.filter(notebookId=notebookStatuses[i]["id"]).first()
            if notebookJob:
                notebookStatuses[i]["isScheduled"] = True
                notebookStatuses[i]["schedule"] = str(notebookJob.crontab)
            else:
                notebookStatuses[i]["isScheduled"] = False
        res.update(True, "NotebookJobs retrieved successfully", notebookStatuses)
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