import pytest
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models import Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_armaments_concession_earns_revenue_when_legions_raised(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.state_treasury = 100
    game.save()

    senator = Senator.objects.get(game=game, name="Cornelius")
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
    execute_effects_and_manage_actions(game.id)

    # Assert
    senator.refresh_from_db()
    # 5 legions * 2T per legion = 10T
    assert senator.talents == 10

    expected_message = f"{senator.display_name} earned 10T from the armaments concession."
    assert game.logs.filter(text=expected_message).count() == 1


@pytest.mark.django_db
def test_ship_building_concession_earns_revenue_when_fleets_raised(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.state_treasury = 100
    game.save()

    senator = Senator.objects.get(game=game, name="Julius")
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
    execute_effects_and_manage_actions(game.id)

    # Assert
    senator.refresh_from_db()
    # 4 fleets * 3T per fleet = 12T
    assert senator.talents == 12

    expected_message = f"{senator.display_name} earned 12T from the ship building concession."
    assert game.logs.filter(text=expected_message).count() == 1
