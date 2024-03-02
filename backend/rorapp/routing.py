from django.urls import re_path
from rorapp.consumers import GameConsumer, InvalidRouteConsumer, PlayerConsumer

websocket_urlpatterns = [
    re_path(r"ws/games/(?P<game_id>\d+)/$", GameConsumer.as_asgi()),
    re_path(r"ws/players/(?P<player_id>\d+)/$", PlayerConsumer.as_asgi()),
    # Catch-all pattern
    re_path(r"^.*$", InvalidRouteConsumer.as_asgi()),
]
