from django.conf import settings

from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.revolt import land_victors_in_declaration_order
from rorapp.models import Game


class RevoltDeclarationNextEffect(EffectBase):
    """Give the faction of the next land victor to declare the decision (1.11.3)."""

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.REVOLT_DECLARATION
            and settings.FEATURE_FLAGS.get("civil_war", False)
            and any(c.land_victory for c in game_state.campaigns)
            and not any(
                f.has_status_item(FactionStatusItem.AWAITING_DECISION)
                for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        commander = land_victors_in_declaration_order(GameStateLive(game_id))[0].commander
        assert commander is not None and commander.faction is not None
        faction = commander.faction
        faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()
        return True
