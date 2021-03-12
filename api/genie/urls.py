from django.urls import path
from . import views

urlpatterns = [
    path("notebookjobs/", views.getNotebookJobs, name="getNotebookJobs"),
    path("notebookjob/", views.addNotebookJob, name="addNotebookJob"),
]
