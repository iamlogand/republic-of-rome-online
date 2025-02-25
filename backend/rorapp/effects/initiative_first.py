from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


class InitiativeFirstEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int) -> None:
        factions = [
            f
            for f in Faction.objects.filter(game=game_id)
            if not f.has_status_item(Faction.StatusItem.DONE)
        ]
        for faction in factions:
            if any(
                s.has_title(Senator.Title.HRAO)
                for s in Senator.objects.filter(
                    game=game_id, faction=faction.id, alive=True
                )
            ):
                faction.add_status_item(Faction.StatusItem.CURRENT_INITIATIVE)
                faction.add_status_item(Faction.StatusItem.initiative(1))

                game = Game.objects.get(id=game_id)
                game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
                game.save()
                return
