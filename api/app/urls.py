"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from utils.proxy import main as zeppelinProxy
from utils.sparkProxy import main as sparkProxy

urlpatterns = [
    path("admin/", admin.site.urls),
    url(r"^api/proxy/*", zeppelinProxy, name="proxy"),
    url(r"^api/spark_proxy/*", sparkProxy, name="proxy"),
    path("api/genie/", include("genie.urls")),
    path("api/system/", include("system.urls")),
    path("api/workflows/", include("workflows.urls")),
    path("api/workspace/", include("workspace.urls")),
]
