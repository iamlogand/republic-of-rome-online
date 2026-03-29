import pytest
from rorapp.actions.advanced_vote import AdvancedVoteAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_split_vote_yea_and_nay_tallied_separately(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    faction: Faction = basic_game.factions.get(position=1)  # 4 senators
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    yea_senators = senators[:2]
    nay_senators = senators[2:]
    expected_yea = sum(s.votes for s in yea_senators)
    expected_nay = sum(s.votes for s in nay_senators)
    initial_votes_yea = basic_game.votes_yea
    initial_votes_nay = basic_game.votes_nay

    payload = {
        **{str(s.id): {"decision": "yea", "bought_votes": 0} for s in yea_senators},
        **{str(s.id): {"decision": "nay", "bought_votes": 0} for s in nay_senators},
    }

    # Act
    result = AdvancedVoteAction().execute(
        basic_game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert result.success
    basic_game.refresh_from_db()
    assert basic_game.votes_yea == initial_votes_yea + expected_yea
    assert basic_game.votes_nay == initial_votes_nay + expected_nay


@pytest.mark.django_db
def test_abstaining_senator_adds_no_votes_to_either_tally(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    faction: Faction = basic_game.factions.get(position=2)  # 3 senators
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    yea_senator = senators[0]
    abstain_senators = senators[1:]
    expected_yea = yea_senator.votes
    initial_votes_yea = basic_game.votes_yea
    initial_votes_nay = basic_game.votes_nay

    payload = {
        str(yea_senator.id): {"decision": "yea", "bought_votes": 0},
        **{str(s.id): {"decision": "abstain", "bought_votes": 0} for s in abstain_senators},
    }

    # Act
    result = AdvancedVoteAction().execute(
        basic_game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert result.success
    basic_game.refresh_from_db()
    assert basic_game.votes_yea == initial_votes_yea + expected_yea
    assert basic_game.votes_nay == initial_votes_nay


@pytest.mark.django_db
def test_senator_status_items_set_per_decision(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    faction: Faction = basic_game.factions.get(position=2)  # exactly 3 senators
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    yea_senator, nay_senator, abstain_senator = senators

    payload = {
        str(yea_senator.id): {"decision": "yea", "bought_votes": 0},
        str(nay_senator.id): {"decision": "nay", "bought_votes": 0},
        str(abstain_senator.id): {"decision": "abstain", "bought_votes": 0},
    }

    # Act
    AdvancedVoteAction().execute(
        basic_game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    yea_senator.refresh_from_db()
    nay_senator.refresh_from_db()
    abstain_senator.refresh_from_db()
    assert yea_senator.has_status_item(Senator.StatusItem.VOTED_YEA)
    assert nay_senator.has_status_item(Senator.StatusItem.VOTED_NAY)
    assert abstain_senator.has_status_item(Senator.StatusItem.ABSTAINED)


@pytest.mark.django_db
def test_split_vote_with_bought_votes(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    faction: Faction = basic_game.factions.get(position=2)  # 3 senators
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    yea_senator, nay_senator, abstain_senator = senators
    initial_talents = 5
    bought = 3
    yea_senator.talents = initial_talents
    yea_senator.save()
    initial_votes_yea = basic_game.votes_yea
    initial_votes_nay = basic_game.votes_nay

    payload = {
        str(yea_senator.id): {"decision": "yea", "bought_votes": bought},
        str(nay_senator.id): {"decision": "nay", "bought_votes": 0},
        str(abstain_senator.id): {"decision": "abstain", "bought_votes": 0},
    }

    # Act
    result = AdvancedVoteAction().execute(
        basic_game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert result.success
    basic_game.refresh_from_db()
    assert basic_game.votes_yea == initial_votes_yea + yea_senator.votes + bought
    assert basic_game.votes_nay == initial_votes_nay + nay_senator.votes
    yea_senator.refresh_from_db()
    assert yea_senator.talents == initial_talents - bought
