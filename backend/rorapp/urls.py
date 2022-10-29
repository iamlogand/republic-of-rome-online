from django.urls import path, include
from rest_framework import routers
from rorapp import views

router = routers.DefaultRouter()
router.register(r'games', views.GameView, 'game')

app_name = "rorapp"
urlpatterns = [
    path('', include(router.urls))
]
