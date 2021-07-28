from django.contrib import admin
from workflows.models import Workflow, WorkflowRunLogs, WorkflowNotebookMap

class WorkflowRunLogsAdmin(admin.ModelAdmin):
    # Adding starttimestamp in a new modelAdmin class as its a readonly field
    # to make it visible in the admin panel
    readonly_fields = ('startTimestamp',)


admin.site.register(Workflow)
admin.site.register(WorkflowRunLogs, WorkflowRunLogsAdmin)
admin.site.register(WorkflowNotebookMap)
