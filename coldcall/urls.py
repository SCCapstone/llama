from django.urls import path
from django.contrib import admin

from . import views

app_name = "coldcall"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls)
]