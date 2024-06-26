from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from rorapp import views

router = routers.DefaultRouter()
router.register("factions", views.FactionViewSet, basename="faction")
router.register("games", views.GameViewSet, basename="game")
router.register("players", views.PlayerViewSet, basename="game-player")
router.register("action-logs", views.ActionLogViewSet, basename="action-log")
router.register("phases", views.PhaseViewSet, basename="phase")
router.register("actions", views.ActionViewSet, basename="action")
router.register(
    "secrets-private", views.SecretPrivateViewSet, basename="secret-private"
)
router.register("secrets-public", views.SecretPublicViewSet, basename="secret-public")
router.register("senators", views.SenatorViewSet, basename="senator")
router.register(
    "senator-action-logs", views.SenatorActionLogViewSet, basename="senator-action-log"
)
router.register("steps", views.StepViewSet, basename="step")
router.register("titles", views.TitleViewSet, basename="title")
router.register("turns", views.TurnViewSet, basename="turn")
router.register("users", views.UserViewSet, basename="user")
router.register(
    "waitlist-entries", views.WaitlistEntryViewSet, basename="waitlist-entry"
)
router.register("wars", views.WarViewSet, basename="war")
router.register("enemy-leaders", views.EnemyLeaderViewSet, basename="enemy-leader")
router.register("concessions", views.ConcessionViewSet, basename="concession")

app_name = "rorapp"

urlpatterns = [
    path("", views.index),
    path("api/", include(router.urls)),
    path("api/tokens/", views.MyTokenObtainPairView.as_view(), name="tokens"),
    path("api/tokens/refresh/", TokenRefreshView.as_view(), name="tokens-refresh"),
    path(
        "api/tokens/email/",
        views.TokenObtainPairByEmailView.as_view(),
        name="tokens-email",
    ),
    path(
        "api/games/<int:game_id>/start-game/",
        views.StartGameViewSet.as_view({"post": "start_game"}),
        name="start-game",
    ),
    path(
        "api/games/<int:game_id>/submit-action/<int:action_id>/",
        views.SubmitActionViewSet.as_view({"post": "submit_action"}),
        name="submit-action",
    ),
]
