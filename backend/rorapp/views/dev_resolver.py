import json
import roman

__test__ = False

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from rorapp.helpers.resolver_cache import (
    EMPTY_RESOLVER_STATE,
    _get_resolver_state,
    _resolver_cache_key,
    _save_resolver_state,
    send_resolver_state,
)

VALID_CHIT_CODES = {str(i) for i in range(1, 31)}
VALID_ROMAN = {roman.toRoman(n) for n in range(1, 26)}


@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def test_resolver(request, game_id: int):
    """
    GET    — return the full resolver state (all queues)
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


@csrf_exempt
@require_POST
def test_resolver_enqueue_dice(request, game_id: int):
    """POST — append one dice result (a single positive int) to the dice queue."""
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        values = data["values"]
        if not isinstance(values, list) or len(values) != 1:
            raise ValueError
        value = values[0]
        if not isinstance(value, int) or value < 1:
            return JsonResponse(
                {"detail": "Dice value must be a positive integer"}, status=400
            )
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse(
            {"detail": "values must be a list containing exactly one positive integer"},
            status=400,
        )

    cache_key = _resolver_cache_key(game_id)
    state = _get_resolver_state(cache_key)
    state["dice_rolls"].append(value)
    _save_resolver_state(cache_key, state)
    send_resolver_state(game_id, state)
    return JsonResponse(state)


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
    """POST — append one mortality-chits draw result (list of senator codes 1–30) to the queue."""
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        values = data["values"]
        if not isinstance(values, list) or not values:
            raise ValueError
        invalid = [
            v for v in values if not isinstance(v, str) or v not in VALID_CHIT_CODES
        ]
        if invalid:
            return JsonResponse(
                {"detail": f"Invalid chit codes: {invalid}. Use senator codes 1–30"},
                status=400,
            )
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse(
            {"detail": "values must be a non-empty list of senator codes"}, status=400
        )

    cache_key = _resolver_cache_key(game_id)
    state = _get_resolver_state(cache_key)
    state["mortality_chits"].append(values)
    _save_resolver_state(cache_key, state)
    send_resolver_state(game_id, state)
    return JsonResponse(state)


@csrf_exempt
@require_POST
def test_resolver_enqueue_veteran(request, game_id: int):
    """POST — append one veteran selection (a single legion Roman numeral) to the queue."""
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        values = data["values"]
        if not isinstance(values, list) or len(values) != 1:
            raise ValueError
        value = values[0]
        if not isinstance(value, str) or value.upper() not in VALID_ROMAN:
            return JsonResponse(
                {"detail": "Veteran value must be a Roman numeral I–XXV"}, status=400
            )
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse(
            {"detail": "values must be a list containing exactly one Roman numeral"},
            status=400,
        )

    cache_key = _resolver_cache_key(game_id)
    state = _get_resolver_state(cache_key)
    state["veteran_order"].append(value.upper())
    _save_resolver_state(cache_key, state)
    send_resolver_state(game_id, state)
    return JsonResponse(state)


@csrf_exempt
@require_http_methods(["DELETE"])
def test_resolver_dequeue(request, game_id: int, queue: str, index: int):
    """DELETE — remove one entry from the given queue by index."""
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    field_map = {
        "dice": "dice_rolls",
        "land-casualties": "land_casualty_order",
        "naval-casualties": "naval_casualty_order",
        "chits": "mortality_chits",
        "veteran": "veteran_order",
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
