from django.urls import path, include
from rest_framework import routers
from rorapp import views

router = routers.DefaultRouter()

app_name = "rorapp"

urlpatterns = [
    path("", views.index),
    path("api/", include(router.urls)),
    path("auth-status/", views.auth_status, name="auth_status"),
    path("login-callback/", views.login_callback, name="login_callback"),
]
