from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path("notebooks/<int:offset>", views.NotebookView.as_view(), name="getNotebooks"),
    path("notebookjob/<int:notebookJobId>", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("notebookjob/", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("schedules/", views.ScheduleView.as_view(), name="scheduleView"),
    path("timezones/", views.TimzoneView.as_view(), name="timezoneView")
]
