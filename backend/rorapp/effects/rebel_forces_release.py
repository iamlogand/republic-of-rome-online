from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, War


class RebelForcesReleaseEffect(EffectBase):
    """Prompt the rebel to choose which forces to release when they cannot afford maintenance (§1.11.35)."""

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REBEL_FORCES_RELEASE
            and not any(
                f.has_status_item(FactionStatusItem.AWAITING_DECISION)
                for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        revolt = (
            War.objects.filter(game_id=game_id, primary_rebel__isnull=False)
            .exclude(status=War.Status.DEFEATED)
            .select_related("primary_rebel")
            .first()
        )
        if revolt and revolt.primary_rebel and revolt.primary_rebel.faction_id:
            faction = Faction.objects.get(id=revolt.primary_rebel.faction_id)
            faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
            faction.save()
        return True
