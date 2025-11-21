import pytest
from rest_framework.test import APIClient
from rorapp.models import AvailableAction, Faction, Game
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_vote_actions_available(self, basic_game: Game):

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
def test_can_vote_yea(self, basic_game: Game):

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
    client = APIClient()
    client.force_authenticate(user=faction.player)

    # Act
    response = client.post(
        f"/api/games/{game.id}/submit-action/Vote yea", {}, format="json"
    )

    # Assert
    assert response.status_code == 200
    assert response.data["message"] == "Action submitted"
    faction.refresh_from_db()
    assert faction.has_status_item(Faction.StatusItem.DONE)
    assert not faction.has_status_item(Faction.StatusItem.CALLED_TO_VOTE)
    game.refresh_from_db()
    assert game.votes_yea > initial_votes_yea
