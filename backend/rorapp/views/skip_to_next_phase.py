from django.contrib import messages
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect

from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.send_game_state import send_game_state
from rorapp.models.available_action import AvailableAction
from rorapp.models.game import Game


PHASE_ORDER = [
    Game.Phase.MORTALITY,
    Game.Phase.REVENUE,
    Game.Phase.FORUM,
    Game.Phase.POPULATION,
    Game.Phase.SENATE,
    Game.Phase.COMBAT,
    Game.Phase.REVOLUTION,
]


def skip_to_next_phase_view(
    request, game_id: int
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    game = Game.objects.get(id=game_id)

    # Determine next phase
    if game.phase in (Game.Phase.REVOLUTION, Game.Phase.INITIAL):
        next_phase = Game.Phase.MORTALITY
    else:
        current_index = PHASE_ORDER.index(game.phase)
        next_phase = PHASE_ORDER[current_index + 1]

    # Increment turn when wrapping from revolution to mortality
    if game.phase == Game.Phase.REVOLUTION:
        game.turn += 1

    # Clear transient state
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

    messages.success(
        request,
        f"Skipped to {next_phase} phase.",
    )
    return redirect("admin:rorapp_game_change", object_id=game_id)
