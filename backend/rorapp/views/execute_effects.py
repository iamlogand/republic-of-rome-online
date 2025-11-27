from django.contrib import messages
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect

from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.send_game_state import send_game_state


def execute_effects_view(
    request, game_id: int
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    execute_effects_and_manage_actions(game_id)
    send_game_state(game_id)
    messages.success(
        request,
        f"Effects executed.",
    )
    return redirect("admin:rorapp_game_change", object_id=game_id)
