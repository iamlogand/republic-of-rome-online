import pytest
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


@pytest.mark.django_db
def test_armaments_earns_revenue_when_legions_raised(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    game.state_treasury = 100
    game.save()

    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.add_concession(Concession.ARMAMENTS)
    senator.talents = 0
    senator.save()

    game.current_proposal = "Raise 5 legions"
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.talents == 10


@pytest.mark.django_db
def test_ship_building_earns_revenue_when_fleets_raised(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    game.state_treasury = 100
    game.save()

    senator = Senator.objects.get(game=game, family_name="Julius")
    senator.add_concession(Concession.SHIP_BUILDING)
    senator.talents = 0
    senator.save()

    game.current_proposal = "Raise 4 fleets"
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.talents == 12


@pytest.mark.django_db
def test_armaments_reveals_corrupt_bar_when_forces_raised(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    game.state_treasury = 100
    game.save()

    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.add_concession(Concession.ARMAMENTS)
    senator.save()

    game.current_proposal = "Raise 2 legions"
    game.votes_yea = 20
    game.votes_nay = 0
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.has_corrupt_concession(Concession.ARMAMENTS)
