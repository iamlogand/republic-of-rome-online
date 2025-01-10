from django.urls import path, include
from rest_framework import routers
from rorapp import views

router = routers.DefaultRouter()

app_name = "rorapp"

urlpatterns = [
    path("", views.index),
    path("api/", include(router.urls)),
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
]
