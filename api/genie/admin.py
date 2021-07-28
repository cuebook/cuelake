from django.contrib import admin
from genie.models import NotebookObject, NotebookJob, NotebookRunLogs, Connection, ConnectionType, ConnectionParam, ConnectionParamValue, NotebookTemplate, CustomSchedule


class NotebookRunLogsAdmin(admin.ModelAdmin):
    # Adding starttimestamp in a new modelAdmin class as its a readonly field
    # to make it visible in the admin panel
    readonly_fields = ('startTimestamp','updateTimestamp')

admin.site.register(NotebookJob)
admin.site.register(NotebookObject)
admin.site.register(NotebookRunLogs, NotebookRunLogsAdmin)
admin.site.register(Connection)
admin.site.register(ConnectionType)
admin.site.register(ConnectionParam)
admin.site.register(ConnectionParamValue)
admin.site.register(NotebookTemplate)
admin.site.register(CustomSchedule)
