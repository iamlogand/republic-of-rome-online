import json

__test__ = False

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.send_game_state import send_game_state
from rorapp.models import AvailableAction, Game
from rorapp.views.skip_to_next_phase import PHASE_ORDER


@csrf_exempt
@require_POST
def test_login(request):
    if not settings.DEBUG:
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
    if not settings.DEBUG:
        return JsonResponse({}, status=403)
    game = Game.objects.get(id=game_id)

    if game.phase in (Game.Phase.REVOLUTION, Game.Phase.INITIAL):
        next_phase = Game.Phase.MORTALITY
    else:
        if game.phase is None:
            raise ValueError(f"Game {game_id} has no phase")
        current_index = PHASE_ORDER.index(Game.Phase(game.phase))
        next_phase = PHASE_ORDER[current_index + 1]

    if game.phase == Game.Phase.REVOLUTION:
        game.turn += 1

    AvailableAction.objects.filter(game=game).delete()

    for faction in game.factions.all():
        faction.status_items = []
        faction.save()

    for faction in game.factions.all():
        for senator in faction.senators.all():
            senator.status_items = []
            senator.save()

    game.current_proposal = None
    game.defeated_proposals = []
    game.votes_yea = 0
    game.votes_nay = 0
    game.phase = next_phase
    game.sub_phase = Game.SubPhase.START
    game.save()

    execute_effects_and_manage_actions(game_id)
    send_game_state(game_id)

    game.refresh_from_db()
    return JsonResponse({"phase": game.phase, "sub_phase": game.sub_phase})
