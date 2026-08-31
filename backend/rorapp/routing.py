from django.conf import settings
from django.urls import re_path
from rorapp.consumers import GameConsumer, PlayerConsumer, InvalidRouteConsumer

websocket_urlpatterns = [
    re_path(r"ws/games/(?P<game_id>\d+)/$", GameConsumer.as_asgi()),
    re_path(r"ws/games/(?P<game_id>\d+)/player/$", PlayerConsumer.as_asgi()),
]

if settings.TEST_ENDPOINTS_ENABLED:
    from rorapp.consumers import DebugConsumer

    websocket_urlpatterns.append(
        re_path(r"ws/games/(?P<game_id>\d+)/debug/$", DebugConsumer.as_asgi())
    )

websocket_urlpatterns.append(re_path(r"^.*$", InvalidRouteConsumer.as_asgi()))
