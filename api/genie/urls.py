from django.urls import path
from . import views

urlpatterns = [
    path("notebooks/<int:offset>", views.getNotebooks, name="getNotebooks"),
    path("notebookjob/", views.addNotebookJob, name="addNotebookJob"),
    path("schedules/", views.getSchedules, name="getSchedules"),
]
