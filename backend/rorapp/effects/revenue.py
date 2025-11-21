from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Log, Senator


class RevenueEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)

        # Rome earns revenue
        game.state_treasury += 100
        Log.create_object(
            game_id=game.id,
            text=f"The State earned 100T of revenue.",
        )

        # Senators earn personal revenue
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            senators = Senator.objects.filter(game=game_id, faction=faction, alive=True)
            faction_revenue = 0
            for senator in senators:
                if senator.has_title(Senator.Title.FACTION_LEADER):
                    senator.talents += 3
                    faction_revenue += 3
                else:
                    senator.talents += 1
                    faction_revenue += 1
            Senator.objects.bulk_update(senators, ["talents"])
            Log.create_object(
                game_id=game.id,
                text=f"{faction.display_name} earned {faction_revenue}T of revenue.",
            )

        # Progress game
        game.sub_phase = Game.SubPhase.REDISTRIBUTION
        game.save()
        return True
