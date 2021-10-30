from django.urls import path

from . import views

urlpatterns = [
    path("notebooks/<int:workspaceId>/<int:offset>", views.NotebookView.as_view(), name="notebooks"),
    path("notebooks/archive/<int:workspaceId>", views.ArchivedNotebooksView.as_view(), name="archivedNotebooksView"),
    path("notebooksLight/<int:workspaceId>", views.NotebooksLightView.as_view(), name="notebooksLightView"),
    path("notebook/<str:notebookId>/<int:workspaceId>", views.NotebookOperationsView.as_view(), name="notebookOperations"),
    path("notebook/actions/<str:notebookId>/<int:workspaceId>", views.NotebookActionsView.as_view(), name="notebookActions"),
    path("notebook/<str:notebookId>/archive/<str:notebookName>/<int:workspaceId>", views.ArchiveNotebookView.as_view(), name="archiveNotebookView"),
    path("notebook/<str:notebookId>/unarchive/<str:notebookName>/<int:workspaceId>", views.UnarchiveNotebookView.as_view(), name="unarchiveNotebookView"),
    path("notebook/<int:workspaceId>", views.NotebookView.as_view(), name="notebook"),
    path("notebookObject/<int:notebookObjId>/<int:workspaceId>", views.getNotebookObject, name="notebookObject"),
    path("notebookjob/<str:notebookId>", views.NotebookJobView.as_view(), name="notebookJobView"),
    path("notebookjob/", views.NotebookJobView.as_view(), name="notebooksJobView"),
    path("notebookTemplates/", views.NotebookTemplateView.as_view(), name="notebookTemplateView"),
    path("schedules/", views.ScheduleView.as_view(), name="scheduleView"),
    path("schedules/<int:scheduleId>", views.schedule, name="getSingleSchedule"),
    path("driverAndExecutorStatus/", views.DriverAndExecutorStatus.as_view(), name="driverAndExecutorStatus"),
    path("timezones/", views.TimzoneView.as_view(), name="timezoneView"),
    # =====================================================================================================
    # Connections
    # =====================================================================================================
    path("connections/<int:workspaceId>", views.connections, name="connections"),
    path("connection/<int:connectionId>", views.connection, name="connection"),
    path("connectiontypes", views.connectionTypes, name="connectionTypes"),
    # =====================================================================================================
    # Connections
    # =====================================================================================================
    path("datasetDetails", views.datasetDetails, name="datasetDetails"),
    # =====================================================================================================
    # Tables & Schemas
    # =====================================================================================================
    path("metastoreTables", views.MetastoreTablesView.as_view(), name="metastoreTables"),
    path("metastoreColumns/<int:tableId>" , views.MetastoreColumnsView.as_view(), name="metastoreColumns")
]
