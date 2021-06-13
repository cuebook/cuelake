import logging
from genie.models import NotebookTemplate
from genie.serializers import NotebookTemplateSerializer
from utils.apiResponse import ApiResponse
from utils.druidSpecGenerator import DruidIngestionSpecGenerator

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Name of the celery task which calls the zeppelin api
CELERY_TASK_NAME = "genie.tasks.runNotebookJob"

GET_NOTEBOOKOJECTS_LIMIT = 25
RUN_STATUS_LIMIT = 10


class NotebookTemplateService:

    @staticmethod
    def getNotebookTemplates():
        res = ApiResponse()
        templates = NotebookTemplate.objects.all()
        serializer = NotebookTemplateSerializer(templates, many=True)
        res.update(True, "Connections retrieved successfully", serializer.data)
        return res
    
    @staticmethod
    def getDatasetDetails(datasetLocation):
        """
        Service to fetch S3 dataset details
        :param datasetLocation: Location of the S3 bucket
        """
        res = ApiResponse()
        schema = DruidIngestionSpecGenerator._getSchemaForDatasourceInS3(datasetLocation)
        ingestionSpec = DruidIngestionSpecGenerator.getIngestionSpec(
            datasetLocation=datasetLocation, datasetSchema=schema
        )
        s3DatasetSchema = list(map(lambda x: {"columnName": x.name, "dataType": "TIMESTAMP" if x.physical_type == "INT96" else x.logical_type.type}, schema))
        datasetDetails = {
            "dremioSchema": s3DatasetSchema,
            "druidIngestionSpec": ingestionSpec
        } 
        res.update(True, "Dataset schema retrieved successfully", datasetDetails)
        return res
