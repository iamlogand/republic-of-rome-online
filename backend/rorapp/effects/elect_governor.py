from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.elect_governor import assign_governor
from rorapp.helpers.governor_election import (
    is_governor_proposal,
    parse_governor_proposal,
)
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.models import Game, Log, Province, Senator


class ElectGovernorEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION
            and is_governor_proposal(game_state.game.current_proposal or "")
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        proposal = game.current_proposal or ""

        if game.votes_yea <= game.votes_nay:
            game.add_defeated_proposal(proposal)
            game.save()
            Log.create_object(game_id, f"Motion defeated: {proposal}.")
            handle_unanimous_defeat(game_id)
            clear_proposal_state(game_id)
            return True

        Log.create_object(game_id, f"Motion passed: {proposal}.")
        pairings = parse_governor_proposal(proposal) or []
        senators = list(Senator.objects.filter(game_id=game_id, alive=True))
        for province_name, senator_name in pairings:
            province = Province.objects.get(game_id=game_id, name=province_name)
            senator = next(s for s in senators if s.display_name == senator_name)
            assign_governor(province, senator)
            Log.create_object(
                game_id,
                f"{senator.display_name} was elected governor of {province.name} and left Rome.",
            )

        clear_proposal_state(game_id)
        return True
