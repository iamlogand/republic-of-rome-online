from typing import Any, Dict, List

from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.game_data import get_senator_codes
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.helpers.popular_appeal import (
    ACCUSED_FREED,
    ACCUSED_KILLED,
    popular_appeal_outcome,
)
from rorapp.helpers.assassination_proposal_consequences import death_record
from rorapp.helpers.special_major_prosecution import (
    censor_in_rome,
    conclude_special_major_prosecution,
    current_prosecution,
    implicate_faction_members,
    log_no_heir,
)
from rorapp.helpers.text import pluralize
from rorapp.models import Game, Log, Senator


class SpecialProsecutionAppealEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase
            == Game.SubPhase.SPECIAL_MAJOR_PROSECUTION
            and game_state.game.current_proposal
        ):
            return False

        accused = next(
            (
                s
                for s in game_state.senators
                if s.has_status_item(Senator.StatusItem.ACCUSED)
                and not s.has_status_item(Senator.StatusItem.APPEALED_TO_PEOPLE)
            ),
            None,
        )
        if accused is None or accused.faction is None:
            return False

        faction = accused.faction
        if faction.has_status_item(FactionStatusItem.CALLED_TO_VOTE):
            return True

        # The presiding magistrate's own faction votes without being called
        holds_presiding_magistrate = any(
            s
            for s in game_state.senators
            if s.faction
            and s.faction.id == faction.id
            and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        )
        return (
            holds_presiding_magistrate
            and not faction.has_status_item(FactionStatusItem.DONE)
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        accused = next(
            (
                s
                for s in Senator.objects.filter(game=game_id)
                if s.has_status_item(Senator.StatusItem.ACCUSED)
            ),
            None,
        )
        if accused is None:
            return False

        trial = current_prosecution(game)
        if trial is None:
            return False

        roll = random_resolver.roll_dice(1) + random_resolver.roll_dice(1)
        result = (
            roll
            - trial["target_popularity"]
            - game.count_effect(GameEffect.EVIL_OMENS)
        )
        outcome = popular_appeal_outcome(result)

        if outcome == ACCUSED_KILLED:
            self._mob_kills_accused(
                game_id, accused, trial["target_popularity"], random_resolver
            )
        elif outcome == ACCUSED_FREED:
            self._crowd_frees_accused(game_id, accused, result, random_resolver)
        else:
            self._modify_votes(game_id, accused, int(outcome))

        return True

    def _mob_kills_accused(
        self,
        game_id: int,
        accused: Senator,
        target_popularity: int,
        random_resolver: RandomResolver,
    ) -> None:

        Log.create_object(
            game_id,
            f"{accused.display_name} was forced to appeal to the people, but the mob turned on him. He was killed.",
        )

        faction_id = accused.faction_id
        deaths = [death_record(accused)]
        # An accused killed by the mob is considered to have been guilty (1.09.421)
        kill_senator(accused, CauseOfDeath.MOB, leave_heir=False)
        log_no_heir(game_id, accused)
        deaths += implicate_faction_members(
            game_id, faction_id, target_popularity, random_resolver
        )
        conclude_special_major_prosecution(game_id, deaths)

    def _crowd_frees_accused(
        self,
        game_id: int,
        accused: Senator,
        result: int,
        random_resolver: RandomResolver,
    ) -> None:

        Log.create_object(
            game_id,
            f"{accused.display_name} was forced to appeal to the people and was freed by the crowd.",
        )

        deaths: List[Dict[str, Any]] = []
        excess = result - 11
        if excess > 0:
            # Without a prosecutor, only the Censor is vulnerable to the mob (1.09.421)
            chits = set(random_resolver.draw_mortality_chits(excess))
            censor = censor_in_rome(game_id)
            if censor is not None and get_senator_codes(censor.code)[0] in chits:
                deaths.append(death_record(censor))
                kill_senator(censor, CauseOfDeath.MOB)

        conclude_special_major_prosecution(game_id, deaths)

    def _modify_votes(self, game_id: int, accused: Senator, votes: int) -> None:

        game = Game.objects.get(id=game_id)
        if votes < 0:
            game.votes_yea += abs(votes)
            outcome = f"added {pluralize(abs(votes), 'vote')} for conviction"
        elif votes > 0:
            game.votes_nay += votes
            outcome = f"added {pluralize(votes, 'vote')} against conviction"
        else:
            outcome = "had no effect on the vote"
        game.save()

        accused.add_status_item(Senator.StatusItem.APPEALED_TO_PEOPLE)
        accused.save()

        Log.create_object(
            game_id,
            f"{accused.display_name} was forced to appeal to the people, which {outcome}.",
        )
