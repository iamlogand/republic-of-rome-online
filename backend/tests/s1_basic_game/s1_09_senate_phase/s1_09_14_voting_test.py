import pytest
from rorapp.actions.advanced_vote import AdvancedVoteAction
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import AvailableAction, Faction, Game, Senator


def _call_faction_to_vote(game: Game, proposal: str) -> Faction:
    game.phase = Game.Phase.SENATE
    game.current_proposal = proposal
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    return faction


def _land_bill_pass_proposal(game: Game) -> str:
    sponsor, cosponsor = Senator.objects.filter(game=game, alive=True)[:2]
    return (
        f"Pass type II land bill"
        f" sponsored by {sponsor.display_name}"
        f" and co-sponsored by {cosponsor.display_name}"
    )


def _land_bill_repeal_proposal(game: Game) -> str:
    sponsor = Senator.objects.filter(game=game, alive=True)[0]
    return f"Repeal type II land bill sponsored by {sponsor.display_name}"


@pytest.mark.django_db
def test_faction_votes_added_on_yea_vote(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.current_proposal = "Test proposal"
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    initial_votes_yea = game.votes_yea
    faction_votes = sum(s.votes for s in faction.senators.all())

    # Act
    result = VoteYeaAction().execute(game.id, faction.id, {}, resolver)

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.votes_yea == initial_votes_yea + faction_votes


@pytest.mark.django_db
def test_abstain_available_during_an_ordinary_vote(basic_game: Game):
    # Arrange
    game = basic_game
    _call_faction_to_vote(game, "Test proposal")

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    action_names = [a.name for a in AvailableAction.objects.filter(game=game)]
    assert "Abstain" in action_names


@pytest.mark.django_db
def test_abstain_unavailable_during_land_bill_passage_vote(basic_game: Game):
    # Arrange
    game = basic_game
    _call_faction_to_vote(game, _land_bill_pass_proposal(game))

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    action_names = [a.name for a in AvailableAction.objects.filter(game=game)]
    assert "Abstain" not in action_names
    assert "Vote yea" in action_names
    assert "Vote nay" in action_names


@pytest.mark.django_db
def test_abstain_unavailable_during_land_bill_repeal_vote(basic_game: Game):
    # Arrange
    game = basic_game
    _call_faction_to_vote(game, _land_bill_repeal_proposal(game))

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    action_names = [a.name for a in AvailableAction.objects.filter(game=game)]
    assert "Abstain" not in action_names
    assert "Vote yea" in action_names
    assert "Vote nay" in action_names


@pytest.mark.django_db
def test_advanced_vote_rejects_abstention_during_land_bill_passage_vote(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = _call_faction_to_vote(game, _land_bill_pass_proposal(game))
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    payload = {
        str(senators[0].id): {"decision": "abstain", "bought_votes": 0},
        **{str(s.id): {"decision": "yea", "bought_votes": 0} for s in senators[1:]},
    }

    # Act
    result = AdvancedVoteAction().execute(
        game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert not result.success
    game.refresh_from_db()
    assert game.votes_yea == 0
    assert not faction.has_status_item(FactionStatusItem.DONE)
    senators[0].refresh_from_db()
    assert not senators[0].has_status_item(Senator.StatusItem.ABSTAINED)


@pytest.mark.django_db
def test_advanced_vote_rejects_abstention_during_land_bill_repeal_vote(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = _call_faction_to_vote(game, _land_bill_repeal_proposal(game))
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    payload = {str(s.id): {"decision": "abstain", "bought_votes": 0} for s in senators}

    # Act
    result = AdvancedVoteAction().execute(
        game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert not result.success
    assert result.message == "Abstaining is not allowed during a land bill vote."


@pytest.mark.django_db
def test_advanced_vote_allows_split_yea_and_nay_during_land_bill_vote(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = _call_faction_to_vote(game, _land_bill_pass_proposal(game))
    senators = list(faction.senators.filter(alive=True).order_by("id"))
    yea_senators = senators[:1]
    nay_senators = senators[1:]
    payload = {
        **{str(s.id): {"decision": "yea", "bought_votes": 0} for s in yea_senators},
        **{str(s.id): {"decision": "nay", "bought_votes": 0} for s in nay_senators},
    }

    # Act
    result = AdvancedVoteAction().execute(
        game.id, faction.id, {"senator_votes": payload}, resolver
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.votes_yea == sum(s.votes for s in yea_senators)
    assert game.votes_nay == sum(s.votes for s in nay_senators)
