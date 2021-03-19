import asyncio
import json
from django_celery_beat.models import CrontabSchedule
from genie.models import NotebookJob, RunStatus
from genie.serializers import NotebookJobSerializer, CrontabScheduleSerializer
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import ZeppelinAPI

# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"
GET_NOTEBOOKJOBS_LIMIT = 10

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
    async def _fetchNotebookStatuses(notebooks: list):
        """
        Async method to fetch notebook status details for multiple notebooks
        Returns a dict with notebook ids as keys
        :param notebooks: List of notebook describing dicts each containing the 'id' field
        """
        zeppelinApiObj = ZeppelinAPI()
        notebookStatuses = {}
        for future in asyncio.as_completed([zeppelinApiObj.getNotebookStatus(notebook["id"]) for notebook in notebooks]):
            status = await future
            notebookStatuses[status["id"]] = status
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
        for notebook in notebooks:
            notebook["name"] = notebook["path"]
            notebookJob = NotebookJob.objects.filter(notebookId=notebook["id"]).first()
            if notebookJob:
                notebook["isScheduled"] = True
                notebook["schedule"] = str(notebookJob.crontab)
                lastScheduledRun = RunStatus.objects.filter(notebookJob=notebookJob).last()
                if lastScheduledRun and lastScheduledRun.status != "RUNNING":
                    notebook["lastScheduledRun"] = True
                    notebook.update(json.loads(lastScheduledRun.logs))
                else:
                    notebook["lastScheduledRun"] = False
            else:
                notebook["isScheduled"] = False
                notebook["lastScheduledRun"] = False
        zeppelinNotebookStatuses = asyncio.run(NotebookJobServices._fetchNotebookStatuses([note for note in notebooks if not note["lastScheduledRun"]]))
        for notebook in notebooks:
            if not notebook["lastScheduledRun"]:
                notebook.update(zeppelinNotebookStatuses[notebook["id"]])
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

    @staticmethod
    def getSchedules():
        """
        Service to get all schedules
        """
        res = ApiResponse()
        crontabSchedules = CrontabSchedule.objects.all()
        data = CrontabScheduleSerializer(crontabSchedules, many=True).data
        res.update(True, "Schedules fetched successfully", data)
        return res