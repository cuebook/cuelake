from django.contrib import admin
from workflows.models import Workflow, WorkflowRun, NotebookJob

admin.site.register(Workflow)
admin.site.register(WorkflowRun)
admin.site.register(NotebookJob)
