from django.urls import re_path
from rorapp.consumers import (
    GameConsumer,
    PlayerConsumer,
    InvalidRouteConsumer,
)

websocket_urlpatterns = [
    re_path(r"ws/games/(?P<game_id>\d+)/$", GameConsumer.as_asgi()),
    re_path(r"ws/games/(?P<game_id>\d+)/player/$", PlayerConsumer.as_asgi()),
    re_path(r"^.*$", InvalidRouteConsumer.as_asgi()),
]
