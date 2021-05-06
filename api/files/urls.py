from django.urls import path
from . import views

urlpatterns = [
    path("files/<int:offset>", views.Files.as_view(), name="files"),
    path("file/<str:key>", views.File.as_view(), name="files"),
    path("file", views.File.as_view(), name="file"),
]
