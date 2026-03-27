import json

__test__ = False

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rorapp.helpers.phase_transition import advance_to_next_phase


@csrf_exempt
@require_POST
def test_login(request):
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    data = json.loads(request.body)
    username = data["username"]
    user, created = User.objects.get_or_create(username=username)
    if created or not user.has_usable_password():
        user.set_password(data.get("password", "password123"))
        user.save()
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    csrf_token = get_token(request)
    return JsonResponse(
        {"id": user.id, "username": user.username, "csrf_token": csrf_token}
    )


@csrf_exempt
@require_POST
def test_skip_to_next_phase(request, game_id: int):
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    game, _ = advance_to_next_phase(game_id)
    return JsonResponse({"phase": game.phase, "sub_phase": game.sub_phase})
