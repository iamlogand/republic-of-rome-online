import pytest
from rorapp.actions.vote_call_faction import VoteCallFactionAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_vote_call_faction_creates_multiple_actions(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = "Deploy forces"
    game.save()

    factions = list(Faction.objects.filter(game=game))
    presiding_faction = factions[0]
    callable_faction_1 = factions[1]
    callable_faction_2 = factions[2]

    callable_faction_2.add_status_item(Faction.StatusItem.DONE)
    callable_faction_2.save()

    presiding_magistrate = Senator.objects.filter(
        game=game, faction=presiding_faction
    ).first()
    assert presiding_magistrate
    presiding_magistrate.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    presiding_magistrate.save()

    snapshot = GameStateSnapshot(game.id)
    action = VoteCallFactionAction()

    # Act
    result = action.get_schema(snapshot, presiding_faction.id)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 1

    available_action = result[0]
    assert available_action.base_name == "Call faction to vote"
    assert (
        available_action.variant_name
        == f"Call {callable_faction_1.display_name} to vote"
    )
    assert available_action.name == f"Call {callable_faction_1.display_name} to vote"
    assert available_action.schema == []
    assert available_action.context == {"target_faction_id": callable_faction_1.id}


@pytest.mark.django_db
def test_vote_call_faction_execute_with_context(basic_game: Game):
    # Arrange
    game = basic_game
    factions = list(Faction.objects.filter(game=game))
    target_faction = factions[1]

    action = VoteCallFactionAction()
    selection = {"target_faction_id": str(target_faction.id)}

    # Act
    result = action.execute(
        game.id,
        factions[0].id,
        selection,
        FakeRandomResolver(),
    )

    # Assert
    assert result.success
    target_faction.refresh_from_db()
    assert target_faction.has_status_item(Faction.StatusItem.CALLED_TO_VOTE)


@pytest.mark.django_db
def test_vote_call_faction_no_actions_when_all_done(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = "Deploy forces"
    game.save()

    factions = list(Faction.objects.filter(game=game))
    presiding_faction = factions[0]

    for faction in factions[1:]:
        faction.add_status_item(Faction.StatusItem.DONE)
        faction.save()

    presiding_magistrate = Senator.objects.filter(
        game=game, faction=presiding_faction
    ).first()
    assert presiding_magistrate
    presiding_magistrate.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    presiding_magistrate.save()

    snapshot = GameStateSnapshot(game.id)
    action = VoteCallFactionAction()

    # Act
    result = action.get_schema(snapshot, presiding_faction.id)

    # Assert
    assert result == []
