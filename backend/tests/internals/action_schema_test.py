import pytest
from rorapp.actions.vote_call_faction import VoteCallFactionAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_vote_call_faction_creates_action_for_each_uncalled_faction(basic_game: Game):
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

    callable_faction_2.add_status_item(FactionStatusItem.DONE)
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
    assert available_action.variant_name == f"Call {callable_faction_1.display_name} to vote"
    assert available_action.schema == []
    assert available_action.context == {"target_faction_id": callable_faction_1.id}


@pytest.mark.django_db
def test_vote_call_faction_executes_and_marks_faction_called(basic_game: Game):
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
    assert target_faction.has_status_item(FactionStatusItem.CALLED_TO_VOTE)


@pytest.mark.django_db
def test_vote_call_faction_returns_no_actions_when_all_factions_done(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = "Deploy forces"
    game.save()

    factions = list(Faction.objects.filter(game=game))
    presiding_faction = factions[0]

    for faction in factions[1:]:
        faction.add_status_item(FactionStatusItem.DONE)
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


@pytest.mark.django_db
def test_vote_actions_available_when_faction_called_to_vote(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.current_proposal = "Test proposal"
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    action_names = [a.name for a in AvailableAction.objects.filter(game=game)]
    assert "Vote yea" in action_names
    assert "Vote nay" in action_names
    assert "Abstain" in action_names
