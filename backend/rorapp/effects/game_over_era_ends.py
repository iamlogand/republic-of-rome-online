from django.utils.timezone import now
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import format_list
from rorapp.models import Faction, Game, Log, Senator


class GameOverEraEndsEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.ERA_ENDS
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        factions = list(Faction.objects.filter(game=game_id).order_by("position"))

        # Compute faction influence totals
        def faction_influence(faction):
            return sum(
                s.influence
                for s in Senator.objects.filter(
                    game=game_id, faction=faction, alive=True
                )
            )

        influence_map = {f.id: faction_influence(f) for f in factions}
        max_inf = max(influence_map.values(), default=0)
        winners = [f for f in factions if influence_map[f.id] == max_inf]

        # Tie-breaker 1: highest individual senator influence
        if len(winners) > 1:

            def max_senator_inf(faction):
                return max(
                    (
                        s.influence
                        for s in Senator.objects.filter(
                            game=game_id, faction=faction, alive=True
                        )
                    ),
                    default=0,
                )

            best = max(max_senator_inf(f) for f in winners)
            winners = [f for f in winners if max_senator_inf(f) == best]

        # Tie-breaker 2: total votes
        if len(winners) > 1:

            def faction_votes(faction):
                return sum(
                    s.votes
                    for s in Senator.objects.filter(
                        game=game_id, faction=faction, alive=True
                    )
                )

            best = max(faction_votes(f) for f in winners)
            winners = [f for f in winners if faction_votes(f) == best]

        game.finished_on = now()
        game.save()
        influence = influence_map[winners[0].id]
        if len(winners) == 1:
            message = f"The era has ended! {winners[0].display_name} wins with {influence} influence."
        else:
            names = format_list([f.display_name for f in winners])
            message = f"The era has ended! {names} share the win with {influence} influence each."
        Log.create_object(game_id, message)
        return True
