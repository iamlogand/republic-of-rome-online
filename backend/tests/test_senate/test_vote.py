import pytest
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import AvailableAction, Faction, Game
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.views.submit_action import SubmitActionViewSet


@pytest.mark.django_db
def test_vote_actions_available(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.current_proposal = "Test proposal"
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(Faction.StatusItem.CALLED_TO_VOTE)
    faction.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    action_names = [a.name for a in AvailableAction.objects.filter(game=game)]
    assert "Vote yea" in action_names
    assert "Vote nay" in action_names
    assert "Abstain" in action_names


@pytest.mark.django_db
def test_can_vote_yea(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.current_proposal = "Test proposal"
    game.save()
    initial_votes_yea = game.votes_yea
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(Faction.StatusItem.CALLED_TO_VOTE)
    faction.save()

    execute_effects_and_manage_actions(game.id)

    # This fake random resolver is not actually needed, but it's here
    # to serve as an example until another test actually needs one
    # TODO: remove fake random resolver to simplify this test
    fake_resolver = FakeRandomResolver()
    factory = APIRequestFactory()
    request = factory.post(
        f"/api/games/{game.id}/submit-action/Vote yea", {}, format="json"
    )
    force_authenticate(request, user=faction.player)
    view = SubmitActionViewSet.as_view({"post": "submit_action"})

    # Act
    response = view(
        request, game_id=game.id, action_name="Vote yea", random_resolver=fake_resolver
    )

    # Assert
    assert response.status_code == 200
    assert response.data["message"] == "Action submitted"
    faction.refresh_from_db()
    assert faction.has_status_item(Faction.StatusItem.DONE)
    assert not faction.has_status_item(Faction.StatusItem.CALLED_TO_VOTE)
    game.refresh_from_db()
    faction_votes = sum(s.votes for s in faction.senators.all())
    assert game.votes_yea == initial_votes_yea + faction_votes
