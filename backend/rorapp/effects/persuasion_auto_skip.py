from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.persuasion_success_chance import persuasion_success_chance
from rorapp.models import Game, Senator


class PersuasionAutoSkipEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PERSUASION_ATTEMPT
        ):
            return False

        current_faction = next(
            (
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)
            ),
            None,
        )
        if not current_faction:
            return False

        persuaders = [
            s
            for s in game_state.senators
            if s.faction_id == current_faction.id and s.alive and s.location == "Rome"
        ]
        if not persuaders:
            return True

        targets = [
            s
            for s in game_state.senators
            if s.alive
            and s.location == "Rome"
            and s.faction_id != current_faction.id
            and not (
                s.faction_id is not None
                and Senator.Title.FACTION_LEADER.value in s.titles
            )
        ]
        if not targets:
            return True

        best_persuader_score = max(
            s.oratory + s.influence + s.talents for s in persuaders
        )
        min_target_score = min(
            s.loyalty + s.talents + (7 if s.faction_id else 0) for s in targets
        )
        best_modifier = best_persuader_score - min_target_score
        threshold = 9 if game_state.game.era_ends else 10
        return persuasion_success_chance(best_modifier, threshold) == 0

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
        game.save()
        return True
