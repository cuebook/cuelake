from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path("notebooks/<int:offset>", views.getNotebooks, name="getNotebooks"),
    path("notebookjob/<int:notebookJobId>", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("notebookjob/", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("schedules/", views.getSchedules, name="getSchedules"),
]
