from django.contrib import admin
from genie.models import NotebookJob, RunStatus

admin.site.register(NotebookJob)
admin.site.register(RunStatus)

# Register your models here.
