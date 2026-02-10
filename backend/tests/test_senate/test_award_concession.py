import pytest
from rorapp.actions.propose_awarding_concession import ProposeAwardingConcessionAction
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


test_resolver = FakeRandomResolver()


@pytest.mark.django_db
def test_propose_awarding_concession(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.add_concession(Concession.MINING)
    game.save()

    senator = Senator.objects.get(game=game, name="Cornelius")
    senator.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senator.save()

    target_senator = Senator.objects.get(game=game, name="Julius")

    action = ProposeAwardingConcessionAction()

    # Act
    result = action.execute(
        game.id,
        senator.faction.id,
        {"Concession": Concession.MINING.value, "Senator": str(target_senator.id)},
        test_resolver,
    )

    # Assert
    assert result.success is True
    game.refresh_from_db()
    assert game.current_proposal == f"Award the mining concession to {target_senator.display_name}"


@pytest.mark.django_db
def test_proposal_award_concession_effect_pass(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.add_concession(Concession.MINING)
    game.save()

    senator = Senator.objects.get(game=game, name="Julius")

    game.current_proposal = f"Award the mining concession to {senator.display_name}"
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.current_proposal is None
    assert Concession.MINING.value not in game.concessions

    senator.refresh_from_db()
    assert senator.has_concession(Concession.MINING)

    assert game.logs.filter(text__contains="received the mining concession").count() == 1


@pytest.mark.django_db
def test_proposal_award_concession_effect_fail(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.add_concession(Concession.MINING)
    game.save()

    senator = Senator.objects.get(game=game, name="Julius")

    game.current_proposal = f"Award the mining concession to {senator.display_name}"
    game.votes_yea = 0
    game.votes_nay = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.current_proposal is None
    assert Concession.MINING.value in game.concessions

    senator.refresh_from_db()
    assert not senator.has_concession(Concession.MINING)

    assert f"Award the mining concession to {senator.display_name}" in game.defeated_proposals


@pytest.mark.django_db
def test_propose_awarding_concession_not_available_without_concessions(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.concessions = []
    game.save()

    senator = Senator.objects.get(game=game, name="Cornelius")
    senator.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senator.save()

    action = ProposeAwardingConcessionAction()
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = action.is_allowed(snapshot, senator.faction.id)

    # Assert
    assert result is None
