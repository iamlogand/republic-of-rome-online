from django.utils.timezone import now

from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import get_civil_war, standing_rebel
from rorapp.helpers.consul_for_life import get_consul_for_life
from rorapp.helpers.rebel_end_game import (
    BATTLE_WON,
    MAXIMUM_ACTIVE_WARS,
    active_wars_against_rome,
    muster_every_force_for_the_rebel,
    rebel_campaign,
    rebel_faction_name,
)
from rorapp.helpers.text import pluralize
from rorapp.models import Game, Log, Senator


def _finish(game_id: int, text: str) -> None:
    game = Game.objects.get(id=game_id)
    game.finished_on = now()
    game.save()
    Log.create_object(game_id, text)


class RebelEndGameStartEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.rebel_winning_condition > 0
            and game_state.game.sub_phase != Game.SubPhase.REBEL_END_GAME
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        wars = active_wars_against_rome(game_id)
        rebel = standing_rebel(game_id)
        rebel_name = rebel.display_name if rebel else "The rebels"

        # A rebel wins outright if Rome faces fewer than four wars (1.12.3)
        if len(wars) < MAXIMUM_ACTIVE_WARS:
            _finish(
                game_id,
                f"Game over! {rebel_name} seized Rome, so "
                f"{rebel_faction_name(game_id)} wins.",
            )
            return True

        Log.create_object(
            game_id,
            f"{rebel_name} seized a Rome besieged by "
            f"{pluralize(len(wars), 'war')}, and must now defend her to win.",
        )
        muster_every_force_for_the_rebel(game_id)

        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.COMBAT
        game.sub_phase = Game.SubPhase.REBEL_END_GAME
        game.save()
        return True


class RebelEndGameResolutionEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.REBEL_END_GAME
        ):
            return False
        if any(
            s.has_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE)
            for s in game_state.senators
        ):
            return False
        return _outcome(game_state.game.id) is not None

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        outcome = _outcome(game_id)
        rebel = standing_rebel(game_id)
        rebel_name = rebel.display_name if rebel else "The rebels"

        if outcome == "won":
            _finish(
                game_id,
                f"Game over! {rebel_name} drove Rome's wars back below four, so "
                f"{rebel_faction_name(game_id)} wins.",
            )
        elif outcome == "consul for life":
            consul_for_life = get_consul_for_life(
                Senator.objects.filter(game=game_id, alive=True)
            )
            faction_name = (
                consul_for_life.faction.display_name
                if consul_for_life and consul_for_life.faction
                else "Rome"
            )
            _finish(
                game_id,
                f"Game over! {rebel_name} fell in the last battle, so "
                f"{faction_name} wins with its Consul for Life.",
            )
        elif outcome == "revolt failed":
            war = get_civil_war(game_id)
            if war:
                war.delete()
            game = Game.objects.get(id=game_id)
            game.rebel_winning_condition = 0
            game.phase = Game.Phase.COMBAT
            game.sub_phase = Game.SubPhase.END
            game.save()
            Log.create_object(
                game_id,
                f"{rebel_name} fell in the last battle with no Consul for Life to "
                "take Rome, so the revolt failed and the Republic endured.",
            )
        else:
            _finish(
                game_id,
                f"Game over! {rebel_name} could not drive Rome's wars back below "
                "four, and the Republic collapsed.",
            )
        return True


def _outcome(game_id: int):
    """How the Rebel End Game ended, or None while it is still being fought (1.12.3)."""

    game = Game.objects.get(id=game_id)
    rebel = standing_rebel(game_id)
    campaign = rebel_campaign(game_id)
    wars = active_wars_against_rome(game_id)

    # A war that survived the rebel's attack ends his run (1.12.3)
    if campaign and campaign.war_id is not None:
        return "lost"

    if rebel and rebel.alive:
        return "won" if len(wars) < MAXIMUM_ACTIVE_WARS else None

    if len(wars) >= MAXIMUM_ACTIVE_WARS:
        return "lost"
    if game.rebel_winning_condition != BATTLE_WON:
        return "won"
    consul_for_life = get_consul_for_life(
        Senator.objects.filter(game=game_id, alive=True)
    )
    return "consul for life" if consul_for_life else "revolt failed"
