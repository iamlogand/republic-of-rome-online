from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


class InitialPhaseDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.INITIAL
            and game_state.game.sub_phase == Game.SubPhase.FACTION_LEADER
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        # Remove done status and give AWAITING_DECISION to the HRAO faction
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.DONE)
            if any(
                s.has_title(Senator.Title.HRAO)
                for s in Senator.objects.filter(game=game_id, faction=faction.id, alive=True)
            ):
                faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
        Faction.objects.bulk_update(factions, ["status_items"])

        # Advance to initial play cards phase
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
        game.save()
        return True
