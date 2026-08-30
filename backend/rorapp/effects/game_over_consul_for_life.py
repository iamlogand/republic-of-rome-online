from django.utils.timezone import now

from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.consul_for_life import get_consul_for_life
from rorapp.models import Game, Log


class GameOverConsulForLifeEffect(EffectBase):

    # The Consul for Life wins if he survives to the end of a Revolution Phase (1.12.2)
    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
            and get_consul_for_life(game_state.senators) is not None
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        snapshot = GameStateSnapshot(game_id)
        consul_for_life = get_consul_for_life(snapshot.senators)
        if consul_for_life is None or not consul_for_life.faction:
            return False

        game = Game.objects.get(id=game_id)
        game.finished_on = now()
        game.save()

        Log.create_object(
            game_id,
            f"Game over! {consul_for_life.display_name} ruled on as Consul for Life, "
            f"so {consul_for_life.faction.display_name} wins.",
        )

        return True
