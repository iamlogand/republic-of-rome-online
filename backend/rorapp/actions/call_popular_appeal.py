import math
from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.finish_prosecution import finish_prosecution
from rorapp.helpers.kill_senator import kill_senator
from rorapp.helpers.text import pluralize
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


# Popular Appeal Table (result = 2d6 + Popularity)
# Negative values = additional votes FOR conviction; positive = votes AGAINST conviction
def _popular_appeal_table(result: int) -> Any:
    """Returns "killed", "freed", or an int (negative=for conviction, positive=against)."""
    if result <= 0:
        return "killed"
    elif result == 1:
        return -9
    elif result == 2:
        return -7
    elif result == 3:
        return -5
    elif result == 4:
        return -3
    elif result == 5:
        return -1
    elif result == 6:
        return 0
    elif result == 7:
        return 1
    elif result == 8:
        return 3
    elif result == 9:
        return 5
    elif result == 10:
        return 7
    elif result == 11:
        return 9
    else:  # >= 12
        return "freed"


class CallPopularAppealAction(ActionBase):
    NAME = "Call popular appeal"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        if (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.PROSECUTION
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and game_state.game.current_proposal.startswith("Prosecute ")
            and faction.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
            and any(
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_status_item(Senator.StatusItem.ACCUSED)
                and not s.has_status_item(Senator.StatusItem.APPEALED_TO_PEOPLE)
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            return [
                AvailableAction.objects.create(
                    game=snapshot.game,
                    faction=faction,
                    base_name=self.NAME,
                    position=self.POSITION,
                    schema=[],
                )
            ]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        senators = Senator.objects.filter(game=game_id)
        accused = next(
            (s for s in senators if s.has_status_item(Senator.StatusItem.ACCUSED)), None
        )
        prosecutor = next(
            (s for s in senators if s.has_status_item(Senator.StatusItem.PROSECUTOR)),
            None,
        )
        if not accused or not prosecutor:
            return ExecutionResult(False, "No prosecution in progress.")

        faction = Faction.objects.get(game=game_id, id=faction_id)
        is_major = bool(
            game.current_proposal
            and game.current_proposal.endswith("major corruption in office")
        )

        # Roll 2d6 + popularity
        roll = random_resolver.roll_dice(1) + random_resolver.roll_dice(1)
        result = roll + accused.popularity
        table_value = _popular_appeal_table(result)

        if table_value == "killed":
            Log.create_object(
                game_id,
                f"{accused.display_name} called a popular appeal but the mob turned on him. He was killed.",
            )

            accused_had_prior_consul = accused.has_title(Senator.Title.PRIOR_CONSUL)
            accused_influence_before = accused.influence
            kill_senator(game_id, accused.id)

            prosecutor = Senator.objects.get(id=prosecutor.id)
            if accused_had_prior_consul:
                prosecutor.add_title(Senator.Title.PRIOR_CONSUL)
            prosecutor.influence += math.ceil(accused_influence_before / 2)
            prosecutor.save()

            # All factions mark DONE so finish_prosecution can fire
            all_factions = list(Faction.objects.filter(game=game_id))
            for f in all_factions:
                f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
                f.add_status_item(FactionStatusItem.DONE)
            Faction.objects.bulk_update(all_factions, ["status_items"])

            finish_prosecution(game_id, is_major, guilty=True)

        elif table_value == "freed":
            Log.create_object(
                game_id,
                f"{accused.display_name} called a popular appeal and was freed by the crowd.",
            )

            # Mortality chits for each point exceeding 11
            excess = result - 11
            if excess > 0:
                senators = Senator.objects.filter(game=game_id)
                vulnerable = [accused.id, prosecutor.id]
                for _ in range(excess):
                    chits = random_resolver.draw_mortality_chits(1)
                    if chits:
                        chit = chits[0]
                        for senator in senators:
                            if (
                                senator.code == chit
                                and senator.id in vulnerable
                                and senator.alive
                            ):
                                kill_senator(game_id, senator.id)

            # All factions mark DONE
            all_factions = list(Faction.objects.filter(game=game_id))
            for f in all_factions:
                f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
                f.add_status_item(FactionStatusItem.DONE)
            Faction.objects.bulk_update(all_factions, ["status_items"])

            finish_prosecution(game_id, is_major, guilty=False)

        else:
            # Numeric vote modifier — leave resolution to ResolveProsecutionEffect
            vote_modifier = int(table_value)
            if vote_modifier < 0:
                game.votes_yea += abs(vote_modifier)
                direction = f"adding {pluralize(abs(vote_modifier), 'vote')} for conviction"
            elif vote_modifier > 0:
                game.votes_nay += vote_modifier
                direction = f"adding {pluralize(vote_modifier, 'vote')} against conviction"
            else:
                direction = "which had no effect on the vote"

            game.save()

            accused.add_status_item(Senator.StatusItem.APPEALED_TO_PEOPLE)
            accused.save()

            Log.create_object(
                game_id,
                f"{accused.display_name} called a popular appeal, {direction}.",
            )

        return ExecutionResult(True)
