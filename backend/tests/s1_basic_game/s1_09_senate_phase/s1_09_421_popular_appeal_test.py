import pytest
from rorapp.actions.call_popular_appeal import CallPopularAppealAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import AvailableAction, Faction, Game, Senator


@pytest.mark.django_db
def test_popular_appeal_adds_yea_votes(prosecution_setup, resolver: FakeRandomResolver):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup

    cornelius_faction = Faction.objects.get(id=cornelius.faction.id)
    cornelius_faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    cornelius_faction.save()

    cornelius.popularity = 0
    cornelius.add_status_item(Senator.StatusItem.ACCUSED)
    cornelius.save()
    scipio.add_status_item(Senator.StatusItem.PROSECUTOR)
    scipio.save()

    game.current_proposal = f"Prosecute {cornelius.display_name} for corruption in office"
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()

    resolver.dice_rolls = [2, 3]

    # Act
    CallPopularAppealAction().execute(game.id, cornelius_faction.id, {}, resolver)

    # Assert
    game.refresh_from_db()
    assert game.votes_yea == 1


@pytest.mark.django_db
def test_popular_appeal_kills_accused_on_deadly_result(prosecution_setup, resolver: FakeRandomResolver):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup

    cornelius_faction = Faction.objects.get(id=cornelius.faction.id)
    cornelius_faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    cornelius_faction.save()

    cornelius.popularity = -9
    cornelius.add_status_item(Senator.StatusItem.ACCUSED)
    cornelius.save()
    scipio.add_status_item(Senator.StatusItem.PROSECUTOR)
    scipio.save()

    game.current_proposal = f"Prosecute {cornelius.display_name} for corruption in office"
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()

    resolver.dice_rolls = [1, 1]

    # Act
    CallPopularAppealAction().execute(game.id, cornelius_faction.id, {}, resolver)

    # Assert
    cornelius.refresh_from_db()
    is_dead = not cornelius.alive or cornelius.generation > 1
    assert is_dead


@pytest.mark.django_db
def test_popular_appeal_frees_accused_on_high_result(prosecution_setup, resolver: FakeRandomResolver):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup

    cornelius_faction = Faction.objects.get(id=cornelius.faction.id)
    cornelius_faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    cornelius_faction.save()

    cornelius.popularity = 9
    cornelius.add_status_item(Senator.StatusItem.ACCUSED)
    cornelius.save()
    scipio.add_status_item(Senator.StatusItem.PROSECUTOR)
    scipio.save()

    game.current_proposal = f"Prosecute {cornelius.display_name} for corruption in office"
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()

    resolver.dice_rolls = [5, 5]

    # Act
    CallPopularAppealAction().execute(game.id, cornelius_faction.id, {}, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert cornelius.alive
    game.refresh_from_db()
    assert game.current_proposal is None


@pytest.mark.django_db
def test_accused_faction_can_vote_after_popular_appeal(prosecution_setup, resolver: FakeRandomResolver):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup

    cornelius_faction = Faction.objects.get(id=cornelius.faction.id)
    cornelius_faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    cornelius_faction.save()

    cornelius.popularity = 0
    cornelius.add_status_item(Senator.StatusItem.ACCUSED)
    cornelius.save()
    scipio.add_status_item(Senator.StatusItem.PROSECUTOR)
    scipio.save()

    game.current_proposal = f"Prosecute {cornelius.display_name} for corruption in office"
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()

    resolver.dice_rolls = [2, 3]

    # Act
    CallPopularAppealAction().execute(game.id, cornelius_faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    accused_faction_action_names = [
        a.base_name for a in AvailableAction.objects.filter(game=game, faction=cornelius_faction)
    ]
    assert "Vote yea" in accused_faction_action_names
