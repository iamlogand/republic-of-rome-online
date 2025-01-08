from django.urls import re_path
from rorapp.consumers import InvalidRouteConsumer

websocket_urlpatterns = [
    # Catch-all pattern
    re_path(r"^.*$", InvalidRouteConsumer.as_asgi()),
]
