from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Log, Senator


class RollAssassinationDiceEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.ASSASSINATION_RESOLUTION
            and game_state.game.assassination_roll_result == 0
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        senators = list(Senator.objects.filter(game=game_id, alive=True))

        assassin = next(
            (s for s in senators if s.has_status_item(Senator.StatusItem.ASSASSIN)),
            None,
        )
        target = next(
            (
                s
                for s in senators
                if s.has_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
            ),
            None,
        )
        if assassin is None or target is None:
            return False

        roll = random_resolver.roll_dice(1)
        modified = roll + game.assassination_roll_modifier

        game.assassination_roll_result = modified

        if modified <= 2:
            result_text = "Caught"
            assassin.add_status_item(Senator.StatusItem.CAUGHT)
            assassin.save()
        elif modified >= 5:
            result_text = "Killed"
        else:
            result_text = "No effect"

        modifier_text = (
            f" (roll {roll} + modifier {game.assassination_roll_modifier} = {modified})"
            if game.assassination_roll_modifier != 0
            else f" (roll {modified})"
        )
        Log.create_object(
            game_id,
            f"Assassination roll: {result_text}{modifier_text}.",
        )

        # Give the target faction a chance to play Secret Bodyguards if the assassin
        # is not already caught AND the target faction has any cards (hidden information:
        # we don't reveal whether they hold a bodyguard card specifically).
        if modified > 2:
            assert target.faction_id is not None
            target_faction = Faction.objects.get(game=game_id, id=target.faction_id)
            if target_faction.cards:
                target_faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
                target_faction.save()

        game.save()
        return True
