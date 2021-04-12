from django.contrib import admin
from genie.models import NotebookJob, RunStatus


class RunStatusAdmin(admin.ModelAdmin):
    # Adding starttimestamp in a new modelAdmin class as its a readonly field
    # to make it visible in the admin panel
    readonly_fields = ('startTimestamp',)

admin.site.register(NotebookJob)
admin.site.register(RunStatus, RunStatusAdmin)

