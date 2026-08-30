from django.conf import settings
from django.urls import path, include
from rest_framework import routers
from rorapp import views

router = routers.DefaultRouter()
router.register("factions", views.FactionViewSet)
router.register("games", views.GameViewSet)
router.register("users", views.UserViewSet)

app_name = "rorapp"

urlpatterns = [
    path("", views.index),
    path("api/", include(router.urls)),
    path("auth-status/", views.auth_status, name="auth_status"),
    path("login-callback/", views.login_callback, name="login_callback"),
    path(
        "api/games/<int:game_id>/start-game/",
        views.StartGameViewSet.as_view({"post": "start_game"}),
        name="start_game",
    ),
    path(
        "api/games/<int:game_id>/submit-action/<int:action_id>",
        views.SubmitActionViewSet.as_view({"post": "submit_action"}),
        name="submit_action",
    ),
]


if settings.TEST_ENDPOINTS_ENABLED:
    from rorapp.views.test_helpers import (
        test_list_presets,
        test_load_preset,
        test_login,
        test_resolver,
        test_resolver_dequeue,
        test_resolver_enqueue_chits,
        test_resolver_enqueue_dice,
        test_resolver_enqueue_land_casualties,
        test_resolver_enqueue_naval_casualties,
        test_resolver_enqueue_veteran,
    )

    urlpatterns += [
        path("api/test/login/", test_login, name="test_login"),
        path(
            "api/test/presets/",
            test_list_presets,
            name="test_list_presets",
        ),
        path(
            "api/test/load-preset/<int:game_id>/",
            test_load_preset,
            name="test_load_preset",
        ),
        path(
            "api/test/resolver/<int:game_id>/",
            test_resolver,
            name="test_resolver",
        ),
        path(
            "api/test/resolver/<int:game_id>/dice/",
            test_resolver_enqueue_dice,
            name="test_resolver_enqueue_dice",
        ),
        path(
            "api/test/resolver/<int:game_id>/land-casualties/",
            test_resolver_enqueue_land_casualties,
            name="test_resolver_enqueue_land_casualties",
        ),
        path(
            "api/test/resolver/<int:game_id>/naval-casualties/",
            test_resolver_enqueue_naval_casualties,
            name="test_resolver_enqueue_naval_casualties",
        ),
        path(
            "api/test/resolver/<int:game_id>/chits/",
            test_resolver_enqueue_chits,
            name="test_resolver_enqueue_chits",
        ),
        path(
            "api/test/resolver/<int:game_id>/veteran/",
            test_resolver_enqueue_veteran,
            name="test_resolver_enqueue_veteran",
        ),
        path(
            "api/test/resolver/<int:game_id>/<str:queue>/<int:index>/",
            test_resolver_dequeue,
            name="test_resolver_dequeue",
        ),
    ]
