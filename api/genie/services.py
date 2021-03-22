import asyncio
import json
import pytz
from django_celery_beat.models import CrontabSchedule
from genie.models import NotebookJob, RunStatus
from genie.serializers import NotebookJobSerializer, CrontabScheduleSerializer, RunStatusSerializer
from utils.apiResponse import ApiResponse
from utils.zeppelinAPI import ZeppelinAPI

# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"

GET_NOTEBOOKJOBS_LIMIT = 10
RUN_STATUS_LIMIT = 10

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
    def getNotebookJobDetails(notebookJobId: int, runStatusOffset: int = 0):
        """
        Service to fetch run details and logs of the selected NotebookJob
        :param notebookId: ID of the NotebookJob
        :param runStatusOffset: Offset for fetching NotebookJob run statuses
        """
        res = ApiResponse()
        notebookJob = NotebookJob.objects.get(id=notebookJobId)
        notebookJobData = NotebookJobSerializer(notebookJob).data
        runStatuses = notebookJob.runstatus_set.order_by("-timestamp")[runStatusOffset: runStatusOffset + RUN_STATUS_LIMIT]
        notebookJobData["runStatuses"] = RunStatusSerializer(runStatuses, many=True).data
        res.update(True, "NotebookJobs retrieved successfully", notebookJobData)
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
    def updateNotebookJob(notebookJobId: int, crontabScheduleId: int):
        """
        Service to update crontab of an existing NotebookJob
        :param notebookId: ID of the NotebookJob for which to update crontab
        :param crontabScheduleId: ID of CrontabSchedule
        """
        res = ApiResponse()
        crontabScheduleObj = CrontabSchedule.objects.get(id=crontabScheduleId)
        NotebookJob.objects.filter(id=notebookJobId).update(crontab=crontabScheduleObj)
        res.update(True, "NotebookJob updated successfully", None)
        return res

    @staticmethod
    def getSchedules():
        """
        Service to get all CrontabSchedule objects
        """
        res = ApiResponse()
        crontabSchedules = CrontabSchedule.objects.all()
        data = CrontabScheduleSerializer(crontabSchedules, many=True).data
        res.update(True, "Schedules fetched successfully", data)
        return res
    
    @staticmethod
    def addSchedule(cron: str, timezone: str = None):
        """
        Service to add CrontabSchedule
        :param cron: Crontab in string format
        :param timezone: Timezone string for which to configure CrontabSchedule
        """
        res = ApiResponse()
        cronElements = cron.split()
        if len(cronElements) != 5:
            res.update(False, "Crontab must contain five elements")
            return res        
        timezone = timezone if timezone else "UTC"
        CrontabSchedule.objects.create(
            minute=cronElements[0],
            hour=cronElements[1],
            day_of_month=cronElements[2],
            month_of_year=cronElements[3],
            day_of_week=cronElements[4],
            timezone=timezone
        )
        res.update(True, "Schedule added successfully", None)
        return res
    
    @staticmethod
    def getTimezones():
        """
        Service to fetch all pytz timezones
        """
        res = ApiResponse()
        timezones = pytz.all_timezones
        res.update(True, "Timezones fetched successfully", timezones)
        return res
