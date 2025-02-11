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
        "api/games/<int:game_id>/submit-action/<str:action_name>",
        views.SubmitActionViewSet.as_view({"post": "submit_action"}),
        name="submit_action",
    ),
]
