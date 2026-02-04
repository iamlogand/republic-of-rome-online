import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import AvailableAction, Faction, Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.views.submit_action import SubmitActionViewSet


@pytest.mark.django_db
def test_attract_knight_failure(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(StatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    assert senator is not None
    senator.talents = 10
    senator.save()

    execute_effects_and_manage_actions(game.id)

    attract_knight_action = AvailableAction.objects.get(game=game, faction=faction, base_name="Attract knight")

    fake_resolver = FakeRandomResolver()
    fake_resolver.dice_rolls = [2]
    factory = APIRequestFactory()
    request = factory.post(
        f"/api/games/{game.id}/submit-action/{attract_knight_action.id}",
        {"Senator": senator.id, "Talents": 3},
        format="json",
    )
    force_authenticate(request, user=faction.player)
    view = SubmitActionViewSet.as_view({"post": "submit_action"})

    # Act
    response = view(
        request,
        game_id=game.id,
        action_id=attract_knight_action.id,
        random_resolver=fake_resolver,
    )

    # Assert
    assert response.status_code == 200
    assert response.data["message"] == "Action submitted"
    senator.refresh_from_db()
    assert senator.talents == 7
    assert senator.knights == 0
