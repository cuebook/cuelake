from django.urls import path

from . import views

urlpatterns = [
    path("notebooks/<int:offset>", views.NotebookView.as_view(), name="notebookView"),
    path("notebooks/archive", views.ArchivedNotebooksView.as_view(), name="archivedNotebooksView"),
    path("notebooksLight", views.NotebooksLightView.as_view(), name="notebooksLightView"),
    path("notebook/<str:notebookId>", views.NotebookOperationsView.as_view(), name="notebookView"),
    path("notebook/actions/<str:notebookId>", views.NotebookActionsView.as_view(), name="notebookView"),
    path("notebook/<str:notebookId>/archive/<str:notebookName>", views.ArchiveNotebookView.as_view(), name="archiveNotebookView"),
    path("notebook/<str:notebookId>/unarchive/<str:notebookName>", views.UnarchiveNotebookView.as_view(), name="unarchiveNotebookView"),
    path("notebook", views.NotebookView.as_view(), name="notebookView"),
    path("notebookObject/<int:notebookObjId>", views.getNotebookObject, name="notebookObject"),
    path("notebookjob/<str:notebookId>", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("notebookjob/", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("notebookTemplates/", views.NotebookTemplateView.as_view(), name="notebookTemplateView"),
    path("schedules/", views.ScheduleView.as_view(), name="scheduleView"),
    path("schedules/<int:scheduleId>", views.schedule, name="getSingleSchedule"),
    path("driverAndExecutorStatus/", views.DriverAndExecutorStatus.as_view(), name="driverAndExecutorStatus"),
    path("timezones/", views.TimzoneView.as_view(), name="timezoneView"),
    # =====================================================================================================
    # Connections
    # =====================================================================================================
    path("connections", views.connections, name="connections"),
    path("connection/<int:connection_id>", views.connection, name="connection"),
    path("connectiontypes", views.connectionTypes, name="connectionTypes"),
    # =====================================================================================================
    # Connections
    # =====================================================================================================
    path("datasetDetails", views.datasetDetails, name="datasetDetails"),
]
