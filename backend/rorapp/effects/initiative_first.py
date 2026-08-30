from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Log, Senator


class InitiativeFirstEffect(EffectBase):
    """Find the faction with the HRAO and give them the first initiative."""

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        # Passage of time: remove temporary event effects from the forum (§1.07.1)
        game = Game.objects.get(id=game_id)
        permanent_effects = {
            GameEffect.LAND_BILL_2.value,
            GameEffect.LAND_BILL_3.value,
        }
        original_effects = list(game.effects)
        expiring_effects = [
            effect_value
            for effect_value in original_effects
            if effect_value.split(":")[0] not in permanent_effects
        ]
        for effect_value in expiring_effects:
            base_name = effect_value.split(":")[0]
            Log.create_object(game_id, f"The {base_name} has ended.")
        game.effects = [
            effect_value
            for effect_value in original_effects
            if effect_value.split(":")[0] in permanent_effects
        ]
        game.save()

        factions = [
            f
            for f in Faction.objects.filter(game=game_id)
            if not f.has_status_item(FactionStatusItem.DONE)
        ]
        for faction in factions:
            if any(
                s.has_title(Senator.Title.HRAO)
                for s in Senator.objects.filter(
                    game=game_id, faction=faction.id, alive=True
                )
            ):
                faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
                faction.add_initiative(1)
                faction.save()

                game = Game.objects.get(id=game_id)
                game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
                game.save()
                return True
        return False
