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
from rorapp.game_state.send_game_state import send_game_state
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.actions.attract_knight import AttractKnightAction
from rorapp.actions.pressure_knight import PressureKnightAction
from rorapp.models import AvailableAction, Faction, Game, Province, Senator
from rorapp.classes.faction_status_item import FactionStatusItem


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


@csrf_exempt
@require_POST
def test_give_knights(request, game_id: int):
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        knights_to_add = int(data.get("knights", 1))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"detail": "Invalid payload"}, status=400)

    senator = None
    if "senator_id" in data:
        try:
            senator_id = int(data["senator_id"])
            senator = Senator.objects.get(id=senator_id, game_id=game_id, alive=True)
        except (ValueError, TypeError, Senator.DoesNotExist):
            return JsonResponse({"detail": "Senator not found or not alive in this game"}, status=404)
    elif "faction_position" in data:
        try:
            faction_position = int(data["faction_position"])
            faction = Faction.objects.get(game_id=game_id, position=faction_position)
            senator = Senator.objects.filter(
                game_id=game_id, faction=faction, alive=True
            ).order_by("id").first()
            if not senator:
                return JsonResponse({"detail": "No alive senator found for faction"}, status=404)
        except (ValueError, TypeError, Faction.DoesNotExist):
            return JsonResponse({"detail": "Faction not found for given position"}, status=404)
    else:
        return JsonResponse({"detail": "Provide either senator_id or faction_position"}, status=400)

    senator.knights += knights_to_add
    senator.save()

    send_game_state(game_id)

    return JsonResponse({
        "senator_id": senator.id,
        "knights": senator.knights,
    })


@csrf_exempt
@require_POST
def test_enter_attract_knight_with_initiative(request, game_id: int):
    """
    Test-only helper for E2E: Force the game into the exact state needed
    for the Pressure Knight action (and Attract Knight) to be available.

    Sets phase=forum + sub_phase=attract knight, gives CURRENT_INITIATIVE
    to the requested faction (by position), optionally seeds knights on one
    of its senators, directly creates the relevant AvailableAction rows,
    and pushes state. The test then does a page reload to observe the UI.
    """
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        faction_position = int(data["faction_position"])
        knights = int(data.get("knights", 0))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"detail": "Invalid payload: faction_position (int) required"}, status=400)

    try:
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game_id=game_id, position=faction_position)
    except (Game.DoesNotExist, Faction.DoesNotExist):
        return JsonResponse({"detail": "Game or faction not found"}, status=404)

    try:
        # Force the precise sub-phase state required by PressureKnightAction.is_allowed
        game.phase = Game.Phase.FORUM
        game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
        game.save()

        # Clear initiative/status from everyone, then give it only to the target
        for f in Faction.objects.filter(game_id=game_id):
            f.clear_status_items()
            f.save()
        faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
        faction.save()

        # Optionally seed knights on one of the faction's senators
        if knights > 0:
            senator = Senator.objects.filter(
                game_id=game_id, faction=faction, alive=True
            ).order_by("id").first()
            if senator:
                senator.knights += knights
                senator.save()

        # Create exactly the actions needed for this sub-phase (Pressure + Attract for the
        # current initiative holder). We deliberately avoid the full effect executor here
        # because jumping a fresh game straight into ATTRACT_KNIGHT can trigger unrelated
        # effects that aren't prepared for the artificial state.
        AvailableAction.objects.filter(game=game).delete()

        snapshot = GameStateSnapshot(game_id)
        # These will only create AvailableAction rows for factions where is_allowed passes.
        PressureKnightAction().get_schema(snapshot, faction.id)
        AttractKnightAction().get_schema(snapshot, faction.id)

        # The WS push can sometimes fail in test environments (channel layer / Redis
        # connectivity from the WSGI process, or no active consumers). Since the
        # E2E test immediately does a page.reload() afterward, we treat the push
        # as best-effort so we don't turn a successful state mutation into a 500.
        try:
            send_game_state(game_id)
        except Exception:
            # Best effort only — the reload will fetch fresh state via normal paths.
            pass

        return JsonResponse({
            "phase": game.phase,
            "sub_phase": game.sub_phase,
            "faction_position": faction_position,
            "has_current_initiative": faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE),
        })
    except Exception:
        # Return JSON instead of letting Django render a debug HTML page in the test env.
        return JsonResponse(
            {"detail": "Internal error while preparing attract knight state"},
            status=500,
        )


@csrf_exempt
@require_POST
def test_create_forum_provinces(request, game_id: int):
    if not settings.TEST_ENDPOINTS_ENABLED:
        return JsonResponse({}, status=403)

    try:
        data = json.loads(request.body)
        provinces = data["provinces"]
    except (KeyError, TypeError, json.JSONDecodeError):
        return JsonResponse(
            {"detail": "Invalid payload: provinces (list) required"},
            status=400,
        )

    if not isinstance(provinces, list) or not provinces:
        return JsonResponse(
            {"detail": "provinces must be a non-empty list"},
            status=400,
        )

    try:
        Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return JsonResponse({"detail": "Game not found"}, status=404)

    created = []
    for entry in provinces:
        if not isinstance(entry, dict) or "name" not in entry:
            return JsonResponse(
                {"detail": "Each province entry must include a name"},
                status=400,
            )
        name = entry["name"]
        developed = bool(entry.get("developed", False))
        if Province.objects.filter(game_id=game_id, name=name).exists():
            return JsonResponse(
                {"detail": f"Province already exists: {name}"},
                status=400,
            )
        province = Province.objects.create(
            game_id=game_id,
            name=name,
            developed=developed,
        )
        created.append({"id": province.id, "name": province.name, "developed": province.developed})

    send_game_state(game_id)

    return JsonResponse({"provinces": created})
