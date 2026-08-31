from django.db import models

from rorapp.helpers.transfer_power_consuls import transfer_power_consuls
from rorapp.models import Game, Senator


def resume_interrupted_sub_phase(game_id: int) -> None:
    """
    Return the senate to the business that an assassination interrupted, and
    skip past any sub-phase the deaths have made impossible.
    """

    game = Game.objects.get(id=game_id)
    game.sub_phase = game.interrupted_sub_phase
    game.interrupted_sub_phase = ""
    game.assassination_roll_result = 0
    game.assassination_roll_modifier = 0
    game.assassination_target_popularity = 0
    game.bodyguard_rerolls_remaining = 0

    # If returning to dictator appointment but no consuls remain, skip ahead.
    if game.sub_phase == Game.SubPhase.DICTATOR_APPOINTMENT:
        has_consul = Senator.objects.filter(
            game=game_id, alive=True,
        ).filter(
            models.Q(titles__contains=Senator.Title.ROME_CONSUL.value)
            | models.Q(titles__contains=Senator.Title.FIELD_CONSUL.value)
        ).exists()
        if not has_consul:
            game.sub_phase = Game.SubPhase.CENSOR_ELECTION
            game.clear_senate_sub_phase_proposals()

    # If returning to MoH appointment but the Dictator is dead, skip ahead.
    if game.sub_phase == Game.SubPhase.MASTER_OF_HORSE_APPOINTMENT:
        has_dictator = Senator.objects.filter(
            game=game_id, alive=True, titles__contains=Senator.Title.DICTATOR.value
        ).exists()
        if not has_dictator:
            game.sub_phase = Game.SubPhase.CENSOR_ELECTION
            game.clear_senate_sub_phase_proposals()

    # If returning to consular election with only one incoming consul,
    # the survivor automatically becomes Rome Consul.
    if game.sub_phase == Game.SubPhase.CONSULAR_ELECTION:
        incoming = list(Senator.objects.filter(
            game=game_id, alive=True,
            status_items__contains=Senator.StatusItem.INCOMING_CONSUL.value,
        ))
        if len(incoming) == 1:
            game.save()
            transfer_power_consuls(game_id, incoming[0].id)
            return

    game.save()
