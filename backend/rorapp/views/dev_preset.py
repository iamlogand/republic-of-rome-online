import json

__test__ = False

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rorapp.helpers.preset_loader import list_presets, load_preset, resolve_preset
from rorapp.models import Faction, Game


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
def test_list_presets(request):
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    return JsonResponse({"presets": list_presets()})


@csrf_exempt
@require_POST
def test_load_preset(request, game_id: int):
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        preset = data["preset"]
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({"detail": "preset field required"}, status=400)

    available = [p["name"] for p in list_presets()]
    if preset not in available:
        return JsonResponse(
            {"detail": f"Unknown preset '{preset}'. Available: {available}"},
            status=400,
        )

    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return JsonResponse({"detail": "Game not found"}, status=404)

    if Faction.objects.filter(game=game).count() < 3:
        return JsonResponse(
            {"detail": "At least 3 players must join before loading a preset"},
            status=400,
        )

    try:
        with transaction.atomic():
            preset_data = resolve_preset(preset)
            load_preset(game, preset_data)
        return JsonResponse({"game_id": game_id, "preset": preset})
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=500)
