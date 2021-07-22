from django.contrib import admin
from genie.models import NotebookObject, NotebookJob, RunStatus, Connection, ConnectionType, ConnectionParam, ConnectionParamValue, NotebookTemplate, CustomSchedule


class RunStatusAdmin(admin.ModelAdmin):
    # Adding starttimestamp in a new modelAdmin class as its a readonly field
    # to make it visible in the admin panel
    readonly_fields = ('startTimestamp','updateTimestamp')

admin.site.register(NotebookJob)
admin.site.register(NotebookObject)
admin.site.register(RunStatus, RunStatusAdmin)
admin.site.register(Connection)
admin.site.register(ConnectionType)
admin.site.register(ConnectionParam)
admin.site.register(ConnectionParamValue)
admin.site.register(NotebookTemplate)
admin.site.register(CustomSchedule)
