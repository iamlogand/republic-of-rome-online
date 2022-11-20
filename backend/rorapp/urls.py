from django.urls import path, include
from rest_framework import routers
from rorapp import views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

router = routers.DefaultRouter()
router.register(r'games', views.GameViewSet, basename='game')
router.register(r'user', views.UserViewSet, basename='user')
router.register(r'user/detail', views.UserDetailViewSet, basename='user_detail')

app_name = "rorapp"
urlpatterns = [
    path('api/', include(router.urls)),

    # JWT authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/email/', views.TokenObtainPairByEmailView.as_view(), name='token_obtain_pair_by_email'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
