from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from rorapp.views import index

urlpatterns = [
    path('', index),
    path('rorapp/', include('rorapp.urls')),
    path('admin/', admin.site.urls)
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
