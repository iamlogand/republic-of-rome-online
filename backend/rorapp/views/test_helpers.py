import json

__test__ = False

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from rorapp.helpers.preset_loader import list_presets, load_preset, resolve_preset
from rorapp.models import Faction, Game

EMPTY_RESOLVER_STATE: dict = {
    "dice_rolls": [],
    "land_casualty_order": [],
    "naval_casualty_order": [],
    "mortality_chits": [],
}


def _resolver_cache_key(game_id: int) -> str:
    return f"fake_resolver_{game_id}"


def _get_resolver_state(cache_key: str) -> dict:
    return cache.get(cache_key, dict(EMPTY_RESOLVER_STATE))


def _save_resolver_state(cache_key: str, state: dict) -> None:
    if any(state.values()):
        cache.set(cache_key, state)
    else:
        cache.delete(cache_key)


def send_resolver_state(game_id: int, state: dict) -> None:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"debug_{game_id}",
        {"type": "debug_update", "data": {"resolver": state}},
    )


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


@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def test_resolver(request, game_id: int):
    """
    GET    — return the full resolver state (all three queues)
    DELETE — clear everything
    """
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    cache_key = _resolver_cache_key(game_id)

    if request.method == "DELETE":
        cache.delete(cache_key)
        send_resolver_state(game_id, dict(EMPTY_RESOLVER_STATE))
        return JsonResponse(dict(EMPTY_RESOLVER_STATE))

    state = _get_resolver_state(cache_key)
    return JsonResponse(state)


VALID_CHIT_CODES = {str(i) for i in range(1, 31)} | {"none", "draw 2"}


@csrf_exempt
@require_POST
def test_resolver_enqueue_dice(request, game_id: int):
    """POST — append one dice-rolls entry (list of ints 1–6) to the dice queue."""
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        values = data["values"]
        if not isinstance(values, list) or not values:
            raise ValueError
        if not all(isinstance(v, int) and 1 <= v <= 6 for v in values):
            return JsonResponse(
                {"detail": "All dice values must be integers 1–6"}, status=400
            )
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse(
            {"detail": "values must be a non-empty list of integers"}, status=400
        )

    cache_key = _resolver_cache_key(game_id)
    state = _get_resolver_state(cache_key)
    state["dice_rolls"].append(values)
    _save_resolver_state(cache_key, state)
    send_resolver_state(game_id, state)
    return JsonResponse(state)


VALID_ROMAN = {
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
    "XXI",
    "XXII",
    "XXIII",
    "XXIV",
    "XXV",
}


def _enqueue_casualty_order(request, game_id: int, field: str) -> JsonResponse:
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        values = data["values"]
        if not isinstance(values, list) or not values:
            raise ValueError
        invalid = [
            v for v in values if not isinstance(v, str) or v.upper() not in VALID_ROMAN
        ]
        if invalid:
            return JsonResponse(
                {"detail": f"Invalid unit names: {invalid}. Use Roman numerals I–XXV"},
                status=400,
            )
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse(
            {"detail": "values must be a non-empty list of strings"}, status=400
        )

    cache_key = _resolver_cache_key(game_id)
    state = _get_resolver_state(cache_key)
    state[field].append([v.upper() for v in values])
    _save_resolver_state(cache_key, state)
    send_resolver_state(game_id, state)
    return JsonResponse(state)


@csrf_exempt
@require_POST
def test_resolver_enqueue_land_casualties(request, game_id: int):
    """POST — append one land casualty order (legion Roman numerals) to the queue."""
    return _enqueue_casualty_order(request, game_id, "land_casualty_order")


@csrf_exempt
@require_POST
def test_resolver_enqueue_naval_casualties(request, game_id: int):
    """POST — append one naval casualty order (fleet Roman numerals) to the queue."""
    return _enqueue_casualty_order(request, game_id, "naval_casualty_order")


@csrf_exempt
@require_POST
def test_resolver_enqueue_chits(request, game_id: int):
    """POST — append one mortality-chits entry to the chits queue. Valid codes: 1–30, "none", "draw 2"."""
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        values = data["values"]
        if not isinstance(values, list) or not values:
            raise ValueError
        invalid = [
            v
            for v in values
            if not isinstance(v, str) or v.lower() not in VALID_CHIT_CODES
        ]
        if invalid:
            return JsonResponse(
                {
                    "detail": f'Invalid chit codes: {invalid}. Use 1–30, "none", or "draw 2"'
                },
                status=400,
            )
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse(
            {"detail": "values must be a non-empty list of strings"}, status=400
        )

    cache_key = _resolver_cache_key(game_id)
    state = _get_resolver_state(cache_key)
    state["mortality_chits"].append([v.lower() for v in values])
    _save_resolver_state(cache_key, state)
    send_resolver_state(game_id, state)
    return JsonResponse(state)


@csrf_exempt
def test_resolver_dequeue(request, game_id: int, queue: str, index: int):
    """DELETE — remove one entry from the given queue by index."""
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    if request.method != "DELETE":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    field_map = {
        "dice": "dice_rolls",
        "land-casualties": "land_casualty_order",
        "naval-casualties": "naval_casualty_order",
        "chits": "mortality_chits",
    }
    if queue not in field_map:
        return JsonResponse({"detail": "Unknown queue"}, status=404)

    field = field_map[queue]

    cache_key = _resolver_cache_key(game_id)
    state = _get_resolver_state(cache_key)

    if index < 0 or index >= len(state[field]):
        return JsonResponse({"detail": "Index out of range"}, status=404)

    state[field].pop(index)
    _save_resolver_state(cache_key, state)
    send_resolver_state(game_id, state)
    return JsonResponse(state)
