from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rorapp import views

router = routers.DefaultRouter()
router.register('games', views.GameViewSet, basename='game')
router.register('users', views.UsersViewSet, basename='user')
router.register('game-participants', views.GameParticipantViewSet, basename='game-participant')
router.register('waitlist-entry', views.WaitlistEntryViewSet, basename='waitlist-entry')
router.register('family-senator', views.FamilySenatorViewSet, basename='family-senator')
router.register('faction', views.FactionViewSet, basename='faction')

app_name = "rorapp"

urlpatterns = [
    path('', views.index),
    path('api/', include(router.urls)),
    path('api/tokens/', TokenObtainPairView.as_view(), name='tokens'),
    path('api/tokens/refresh/', TokenRefreshView.as_view(), name='tokens-refresh'),
    path('api/tokens/email/', views.TokenObtainPairByEmailView.as_view(), name='tokens-email'),
    path('api/games/<int:pk>/start-game/', views.StartGameViewset.as_view({'post': 'start_game'}), name='start-game')
]
