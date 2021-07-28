import json
from rest_framework import serializers
from genie.models import NotebookObject, NotebookJob, NotebookRunLogs, Connection, ConnectionType, NotebookTemplate, CustomSchedule as Schedule

class NotebookJobSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    class Meta:
        model = NotebookJob
        fields = ["id", "notebookId"]

class NotebookRunLogsSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookRunLogs
    """
    logsJSON = serializers.SerializerMethodField()
    def get_logsJSON(self, obj):
        """
        Gets logs in JSON form
        """
        return json.loads(obj.logs)

    class Meta:
        model = NotebookRunLogs
        fields = ["id", "notebookId", "startTimestamp", "endTimestamp", "status", "logsJSON", "runType"]

class ScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for the model CrontabSchedule
    """
    schedule = serializers.SerializerMethodField()
    crontab = serializers.SerializerMethodField()
    timezone = serializers.SerializerMethodField()
    notebookCount = serializers.SerializerMethodField()
    workflowCount = serializers.SerializerMethodField()
    def get_schedule(self, obj):
        """
        Gets string form of the crontab
        """
        return str(obj)

    def get_timezone(self, obj):
        """ Gets schedule timezone"""
        return str(obj.timezone)

    def cronexp(self, field):
        return field and str(field).replace(' ', '') or '*'
    
    def get_crontab(self, obj):
        """Gets schedule crontab """
        return '{0} {1} {2} {3} {4}'.format(
            self.cronexp(obj.minute), self.cronexp(obj.hour),
            self.cronexp(obj.day_of_month), self.cronexp(obj.month_of_year),
            self.cronexp(obj.day_of_week)
        )
    
    def count(self, obj):
        """Count number of workflow and notebook assinged with schedule  """
        workflow= 0
        notebook = 0
        schedule = Schedule.objects.get(id= obj.id)
        scheduleJob = list(schedule.periodictask_set.values())
        for listItem in scheduleJob:
            if "task" in listItem and listItem["task"] == "genie.tasks.runNotebookJob":
                notebook+=1
            if "task" in listItem and listItem["task"] == "workflows.tasks.runWorkflowJob":
                workflow +=1
        return [notebook,workflow]

    def get_notebookCount(self,obj):
        """Gets assigned notebook count """
        scheduleCount= self.count(obj)
        return scheduleCount[0]

    def get_workflowCount(self, obj):
        """Gets assigned workflow count """
        scheduleCount= self.count(obj)
        return scheduleCount[1]
            

    class Meta:
        model = Schedule
        fields = ["id", "schedule","name","timezone","crontab","notebookCount","workflowCount"]


# Connection Serializers
class ConnectionSerializer(serializers.ModelSerializer):
    connectionTypeId = serializers.SerializerMethodField()
    connectionType = serializers.SerializerMethodField()

    def get_connectionTypeId(self, obj):
        return obj.connectionType.id

    def get_connectionType(self, obj):
        return obj.connectionType.name

    class Meta:
        model = Connection
        fields = [
            "id",
            "name",
            "description",
            "connectionTypeId",
            "connectionType",
        ]


class ConnectionDetailSerializer(serializers.ModelSerializer):
    params = serializers.SerializerMethodField()
    connectionTypeId = serializers.SerializerMethodField()
    connectionType = serializers.SerializerMethodField()

    def get_params(self, obj):
        params = {}
        for val in obj.cpvc.all():
            params[val.connectionParam.name] = val.value if not val.connectionParam.isEncrypted else "**********"
        return params

    def get_connectionTypeId(self, obj):
        return obj.connectionType.id

    def get_connectionType(self, obj):
        return obj.connectionType.name

    class Meta:
        model = Connection
        fields = [
            "id",
            "name",
            "description",
            "params",
            "connectionTypeId",
            "connectionType",
        ]


class ConnectionTypeSerializer(serializers.ModelSerializer):
    
    params = serializers.SerializerMethodField()

    def get_params(self, obj):
        paramList = []
        for param in obj.connectionTypeParam.all():
            params = {}
            params["id"] = param.id
            params["name"] = param.name
            params["label"] = param.label
            params["isEncrypted"] = param.isEncrypted
            params["properties"] = param.properties
            paramList.append(params)
        return paramList

    class Meta:
        model = ConnectionType
        fields = ["id", "name", "params"]


class NotebookTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookJob
    """
    class Meta:
        model = NotebookTemplate
        fields = ["id", "name", "formJson"]


class NotebookObjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the model NotebookObject
    """
    connection = ConnectionDetailSerializer()
    notebookTemplate = NotebookTemplateSerializer()

    class Meta:
        model = NotebookObject
        fields = ["id", "notebookZeppelinId", "defaultPayload", "connection", "notebookTemplate"]