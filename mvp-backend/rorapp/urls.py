from django.urls import path

from rorapp import views

app_name = "rorapp"

urlpatterns = [
    path("", views.index),
]
