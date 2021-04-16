from django.urls import path

from . import views

urlpatterns = [
    path("notebooks/<int:offset>", views.NotebookView.as_view(), name="notebookView"),
    path("notebook/<str:notebookId>", views.NotebookOperationsView.as_view(), name="notebookView"),
    path("notebook", views.NotebookView.as_view(), name="notebookView"),
    path("notebookjob/<int:notebookJobId>", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("notebookjob/", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("notebookTemplates/", views.NotebookTemplateView.as_view(), name="notebookTemplateView"),
    path("schedules/", views.ScheduleView.as_view(), name="scheduleView"),
    path("timezones/", views.TimzoneView.as_view(), name="timezoneView"),
    # =====================================================================================================
    # Connections
    # =====================================================================================================
    path("connections", views.connections, name="connections"),
    path("connection/<int:connection_id>", views.connection, name="connection"),
    path("connectiontypes", views.connectionTypes, name="connectionTypes"),
]
