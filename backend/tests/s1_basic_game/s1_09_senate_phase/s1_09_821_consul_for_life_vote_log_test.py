import pytest

from rorapp.actions.advanced_vote import AdvancedVoteAction
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, Log, Senator


def _make_candidate(game: Game) -> Senator:
    candidate = next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if not s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )
    candidate.influence = 21
    candidate.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    candidate.save()
    return candidate


@pytest.mark.django_db
def test_nominee_influence_is_merged_into_faction_vote_log(
    senate_game: Game, resolver: FakeRandomResolver
):
    game = senate_game
    candidate = _make_candidate(game)
    faction = candidate.faction
    assert faction is not None
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.save()
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()

    VoteYeaAction().execute(game.id, faction.id, {}, resolver)

    bonus_logs = [
        log.text
        for log in Log.objects.filter(game=game)
        if "Consul for Life nominee" in log.text
    ]
    assert len(bonus_logs) == 1
    assert f"Senators in {faction.display_name} voted yea" in bonus_logs[0]
    assert (
        f"{candidate.display_name} added {candidate.influence} votes to his own total "
        "from his influence as the Consul for Life nominee."
        in bonus_logs[0]
    )


@pytest.mark.django_db
def test_nominee_influence_is_merged_into_advanced_vote_log(
    senate_game: Game, resolver: FakeRandomResolver
):
    game = senate_game
    candidate = _make_candidate(game)
    faction = candidate.faction
    assert faction is not None
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.save()
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    faction_senators = list(Senator.objects.filter(game=game, faction=faction))
    selection = {
        "senator_votes": {
            str(s.id): {
                "decision": "nay" if s.id == candidate.id else "abstain",
                "bought_votes": 0,
            }
            for s in faction_senators
        }
    }

    AdvancedVoteAction().execute(game.id, faction.id, selection, resolver)

    bonus_logs = [
        log.text
        for log in Log.objects.filter(game=game)
        if "Consul for Life nominee" in log.text
    ]
    assert len(bonus_logs) == 1
    assert f"Senators in {faction.display_name} split their vote." in bonus_logs[0]
    assert (
        f"{candidate.display_name} added {candidate.influence} votes to his own total "
        "from his influence as the Consul for Life nominee."
        in bonus_logs[0]
    )
