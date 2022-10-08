from django.urls import path
from rorapp.views import index_view, GameView

app_name = "rorapp"
urlpatterns = [
    path("", index_view, name="index"),
    path('games', GameView.as_view(), name='game-list')
]