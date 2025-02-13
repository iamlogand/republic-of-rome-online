from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


class RedistributionDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == "revenue"
            and game_state.game.sub_phase == "redistribution"
            and all("done" in f.status for f in game_state.factions)
        )

    def execute(self, game_id: int) -> None:

        # Remove done status
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.status.remove("done")
        Faction.objects.bulk_update(factions, ["status"])

        # Remove done status
        senators = Senator.objects.filter(game=game_id)
        for senator in senators:
            if "contributed" in senator.status:
                senator.status.remove("contributed")
        Senator.objects.bulk_update(senators, ["status"])

        # Progress game
        game = Game.objects.get(id=game_id)
        game.phase = "revenue"  # TODO: implement the forum phase
        game.sub_phase = "start"
        game.turn += 1
        game.save()
