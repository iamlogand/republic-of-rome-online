from typing import Any, Dict, List, Optional

from django.utils.timezone import now

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.game_data import get_senator_codes
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.helpers.text import format_list
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


def _unrest_change(dice_roll: int) -> Optional[int]:
    """Returns unrest change from the population table, or None for People Revolt."""
    if dice_roll < 0:
        return None
    if dice_roll == 0:
        return 6
    if dice_roll <= 4:
        return 5
    if dice_roll <= 6:
        return 4
    if dice_roll <= 8:
        return 3
    if dice_roll == 9:
        return 2
    if dice_roll <= 15:
        return 0
    if dice_roll == 16:
        return -1
    if dice_roll == 17:
        return -2
    return -3


def _get_adjective(dice_roll: int) -> str:
    if dice_roll <= 3:
        return "a disastrous"
    if dice_roll <= 5:
        return "a terrible"
    if dice_roll <= 7:
        return "a poor"
    if dice_roll <= 9:
        return "a mediocre"
    if dice_roll <= 11:
        return "an adequate"
    if dice_roll <= 13:
        return "a passable"
    if dice_roll <= 15:
        return "a good"
    if dice_roll <= 17:
        return "an impressive"
    return "a masterful"


def _get_reaction_prefix(unrest_change: int) -> str:
    if unrest_change >= 6:
        return "The crowd erupted in violent fury"
    if unrest_change == 5:
        return "The crowd reacted with fierce hostility"
    if unrest_change == 4:
        return "The crowd responded with open outrage"
    if unrest_change == 3:
        return "The crowd responded with scorn and contempt"
    if unrest_change == 2:
        return "The crowd were visibly discontented"
    if unrest_change == 1:
        return "The crowd were mildly displeased"
    if unrest_change == -1:
        return "The crowd received it with cautious approval"
    if unrest_change == -2:
        return "The crowd received it with approval"
    return "The crowd received it with great enthusiasm"


def _get_bridge(dice_result: int, unrest_change: int, popularity: int) -> str:
    good_speech = dice_result >= 14
    bad_speech = dice_result <= 7
    if good_speech and unrest_change >= 0:
        if popularity <= -5:
            return " Even so, the senator was held in deep contempt by the people."
        if popularity >= 5:
            return " Even so, the mood in Rome was beyond even his influence."
        return " Even so, Rome was in no mood to listen."
    if bad_speech and unrest_change <= 0:
        return (
            " Nevertheless, the senator enjoyed considerable goodwill with the people."
        )
    return ""


def _get_reaction(unrest_change: int, actual_unrest_change: int) -> str:
    if unrest_change == 0:
        return " The crowd offered little reaction either way."
    prefix = _get_reaction_prefix(unrest_change)
    if unrest_change > 0:
        return f" {prefix}, causing unrest to increase by {actual_unrest_change}."
    if actual_unrest_change == 0:
        return f" {prefix} and the mood in Rome remained content."
    return f" {prefix}, causing unrest to decrease by {-actual_unrest_change}."


class GiveSpeechAction(ActionBase):
    NAME = "Give speech"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        if not (
            game_state.game.phase == Game.Phase.POPULATION
            and game_state.game.sub_phase == Game.SubPhase.STATE_OF_REPUBLIC_SPEECH
        ):
            return None
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        hrao = next(
            (
                s
                for s in game_state.senators
                if s.alive
                and s.faction_id == faction_id
                and s.has_title(Senator.Title.HRAO)
            ),
            None,
        )
        return faction if hrao else None

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

        senators = list(
            Senator.objects.filter(game=game_id, alive=True, faction__isnull=False)
        )
        hrao = next((s for s in senators if s.has_title(Senator.Title.HRAO)), None)
        if not hrao:
            return ExecutionResult(False, "No HRAO senator found")

        dice_result = random_resolver.roll_dice(3)
        modified_dice_result = dice_result - game.unrest + hrao.popularity
        unrest_change = _unrest_change(modified_dice_result)
        adjective = _get_adjective(dice_result)

        if unrest_change is None:
            message = f"Game over! {hrao.display_name} gave {adjective} State of the Republic speech."
            message += _get_bridge(dice_result, 1, hrao.popularity)
            message += " The people revolted, overthrowing the senatorial government, and the Republic collapsed."
            Log.create_object(game_id, message)
            game.finished_on = now()
            game.save()
            return ExecutionResult(True)

        message = f"{hrao.display_name} gave {adjective} State of the Republic speech."
        message += _get_bridge(dice_result, unrest_change, hrao.popularity)

        # Apply unrest change
        actual_unrest_change = game.change_unrest(unrest_change)
        message += _get_reaction(unrest_change, actual_unrest_change)

        # Manpower shortage and no recruitment
        if modified_dice_result in [0, 1, 2]:
            game.add_effect(GameEffect.NO_RECRUITMENT)
            message += " There will be no recruitment."
        elif modified_dice_result in [3, 5, 7]:
            game.add_effect(GameEffect.MANPOWER_SHORTAGE)
            total_manpower_shortage = game.count_effect(GameEffect.MANPOWER_SHORTAGE)
            if total_manpower_shortage == 1:
                message += " There will be a manpower shortage."
            else:
                message += " The manpower shortage intensified."

        # Mob
        mob_victims: List[Senator] = []
        if modified_dice_result in [0, 1]:
            codes = random_resolver.draw_mortality_chits(6)
            mob_victims = [
                s
                for s in senators
                if s.location == "Rome"
                and get_senator_codes(s.code)[0] in {str(c) for c in codes}
            ]

            if len(mob_victims) >= 2:
                message += f" An outraged mob stormed the Senate, killing {len(mob_victims)} senators."
            elif mob_victims:
                message += f" An outraged mob stormed the Senate, killing a senator."
            else:
                message += (
                    " An outraged mob stormed the Senate, but all senators survived."
                )

        # Single log entry for the entire speech event
        Log.create_object(game_id, message)

        # Kill mob victims
        for victim in mob_victims:
            kill_senator(victim, CauseOfDeath.MOB)

        game.phase = Game.Phase.SENATE
        game.sub_phase = Game.SubPhase.START
        game.save()

        return ExecutionResult(True)
