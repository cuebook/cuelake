from genie.models import NotebookTemplate
from genie.serializers import NotebookTemplateSerializer
from utils.apiResponse import ApiResponse


class NotebookTemplateService:

    @staticmethod
    def getNotebookTemplates():
        res = ApiResponse()
        templates = NotebookTemplate.objects.all()
        serializer = NotebookTemplateSerializer(templates, many=True)
        res.update(True, "Connections retrieved successfully", serializer.data)
        return res
