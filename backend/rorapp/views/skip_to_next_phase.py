from django.contrib import messages
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect

from rorapp.helpers.phase_transition import advance_to_next_phase


def skip_to_next_phase_view(
    request, game_id: int
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    game, next_phase = advance_to_next_phase(game_id)
    messages.success(
        request,
        f"Skipped to {next_phase} phase then resolved to {game.phase} phase.",
    )
    return redirect("admin:rorapp_game_change", object_id=game_id)
