from django.urls import path, include
from django.contrib import admin
from rorapp.views import index

urlpatterns = [
    path('', index),
    path('rorapp/', include('rorapp.urls')),
    path('admin/', admin.site.urls)
]
