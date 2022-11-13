from django.urls import path, include
from rest_framework import routers
from rorapp import views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

router = routers.DefaultRouter()
router.register(r'games', views.GameView, 'game')

app_name = "rorapp"
urlpatterns = [
    path('api/', include(router.urls)),

    # JWT authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/by-email/', views.TokenObtainPairByEmailView.as_view(), name='token_obtain_pair_by_email'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
