from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/games/(?P<game_id>\d+)/$", consumers.GameConsumer.as_asgi()),
]
