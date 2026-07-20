from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.assassination_participants import get_assassination_participants
from rorapp.models import Game, Log, Senator


class BodyguardCatchRerollEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.ASSASSINATION_RESOLUTION
            and game_state.game.bodyguard_rerolls_remaining > 0
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.AWAITING_DECISION)
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        senators = list(Senator.objects.filter(game=game_id, alive=True))

        assassin, _ = get_assassination_participants(senators)
        if assassin is None:
            game.bodyguard_rerolls_remaining = 0
            game.save()
            return True

        roll = random_resolver.roll_dice(1)
        modified = roll + game.assassination_roll_modifier - game.count_effect(GameEffect.EVIL_OMENS)

        if modified <= 2:
            assassin.add_status_item(Senator.StatusItem.CAUGHT)
            assassin.save()
            game.bodyguard_rerolls_remaining = 0
            Log.create_object(
                game_id,
                "Bodyguards caught the assassin!",
            )
        else:
            game.bodyguard_rerolls_remaining -= 1
            Log.create_object(
                game_id,
                "The assassin evaded the bodyguards.",
            )

        game.save()
        return True
