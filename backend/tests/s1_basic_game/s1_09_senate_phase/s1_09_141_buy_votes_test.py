import pytest
from rorapp.actions.advanced_vote import AdvancedVoteAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_bought_votes_added_to_yea_count(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    faction: Faction = basic_game.factions.get(position=2)
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    target = senators[0]
    bought = 2
    target.talents = bought + 1
    target.save()
    base_votes = sum(s.votes for s in senators)
    initial_votes_yea = basic_game.votes_yea

    payload = {
        str(senators[0].id): {"decision": "yea", "bought_votes": bought},
        **{str(s.id): {"decision": "yea", "bought_votes": 0} for s in senators[1:]},
    }

    # Act
    result = AdvancedVoteAction().execute(
        basic_game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert result.success
    basic_game.refresh_from_db()
    assert basic_game.votes_yea == initial_votes_yea + base_votes + bought


@pytest.mark.django_db
def test_bought_votes_deducted_from_senator_talents(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    faction: Faction = basic_game.factions.get(position=2)
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    target = senators[0]
    initial_talents = 5
    bought = 3
    target.talents = initial_talents
    target.save()

    payload = {
        str(senators[0].id): {"decision": "yea", "bought_votes": bought},
        **{str(s.id): {"decision": "yea", "bought_votes": 0} for s in senators[1:]},
    }

    # Act
    AdvancedVoteAction().execute(
        basic_game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    target.refresh_from_db()
    assert target.talents == initial_talents - bought


@pytest.mark.django_db
def test_cannot_buy_more_votes_than_talents(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    faction: Faction = basic_game.factions.get(position=2)
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    senators[0].talents = 1
    senators[0].save()

    payload = {
        str(senators[0].id): {"decision": "yea", "bought_votes": 2},
        **{str(s.id): {"decision": "yea", "bought_votes": 0} for s in senators[1:]},
    }

    # Act
    result = AdvancedVoteAction().execute(
        basic_game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_multiple_senators_buy_votes_independently(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    faction: Faction = basic_game.factions.get(position=2)
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    bought_0, bought_1 = 2, 4
    senators[0].talents = 3
    senators[1].talents = 5
    Senator.objects.bulk_update(senators, ["talents"])
    initial_votes_yea = basic_game.votes_yea

    payload = {
        str(senators[0].id): {"decision": "yea", "bought_votes": bought_0},
        str(senators[1].id): {"decision": "yea", "bought_votes": bought_1},
        str(senators[2].id): {"decision": "yea", "bought_votes": 0},
    }

    # Act
    result = AdvancedVoteAction().execute(
        basic_game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert result.success
    senators[0].refresh_from_db()
    senators[1].refresh_from_db()
    assert senators[0].talents == 3 - bought_0
    assert senators[1].talents == 5 - bought_1
    basic_game.refresh_from_db()
    assert basic_game.votes_yea == initial_votes_yea + sum(s.votes for s in senators) + bought_0 + bought_1
