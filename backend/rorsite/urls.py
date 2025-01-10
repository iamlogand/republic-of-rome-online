from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("", include("rorapp.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
]
