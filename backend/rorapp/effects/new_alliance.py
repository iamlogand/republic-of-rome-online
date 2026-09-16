from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.new_alliance import apply_new_alliance
from rorapp.models import Game, Log, Senator, War


class NewAllianceEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.END
            and game_state.game.has_effect(GameEffect.NEW_ALLIANCE)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        wars = list(
            War.objects.filter(game=game).exclude(status=War.Status.DEFEATED)
        )

        if not wars:
            game.remove_effect(GameEffect.NEW_ALLIANCE)
            game.save()
            Log.create_object(game_id, "The new alliance had no war to end.")
        elif len(wars) == 1:
            apply_new_alliance(game, wars[0], random_resolver)
        else:
            hrao = Senator.objects.select_related("faction").get(
                game=game, alive=True, titles__contains=[Senator.Title.HRAO.value]
            )
            hrao_faction = hrao.faction
            assert hrao_faction is not None
            hrao_faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
            hrao_faction.save()
            game.sub_phase = Game.SubPhase.NEW_ALLIANCE
            game.save()
            Log.create_object(
                game_id, "The HRAO must choose a war for the new alliance to end."
            )
        return True
