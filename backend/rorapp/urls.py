from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from rorapp import views

router = routers.DefaultRouter()
router.register('factions', views.FactionViewSet, basename='faction')
router.register('family-senators', views.FamilySenatorViewSet, basename='family-senator')
router.register('games', views.GameViewSet, basename='game')
router.register('game-participants', views.GameParticipantViewSet, basename='game-participant')
router.register('offices', views.OfficeViewSet, basename='office')
router.register('phases', views.PhaseViewSet, basename='phase')
router.register('steps', views.StepViewSet, basename='step')
router.register('turns', views.TurnViewSet, basename='turn')
router.register('users', views.UserViewSet, basename='user')
router.register('waitlist-entries', views.WaitlistEntryViewSet, basename='waitlist-entry')

app_name = "rorapp"

urlpatterns = [
    path('', views.index),
    path('api/', include(router.urls)),
    path('api/tokens/', views.MyTokenObtainPairView.as_view(), name='tokens'),
    path('api/tokens/refresh/', TokenRefreshView.as_view(), name='tokens-refresh'),
    path('api/tokens/email/', views.TokenObtainPairByEmailView.as_view(), name='tokens-email'),
    path('api/games/<int:pk>/start-game/', views.StartGameViewSet.as_view({'post': 'start_game'}), name='start-game')
]
