from django.urls import path

from . import views

urlpatterns = [
    path("accountsettings/", views.AccountSettingView.as_view(), name="accountSettingView")
]
