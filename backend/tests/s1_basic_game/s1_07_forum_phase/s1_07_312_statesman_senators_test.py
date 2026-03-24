import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War


def _setup_combat(game: Game, war: War) -> Campaign:
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.unrest = 3
    game.save()
    commander = Senator.objects.get(game=game, family_name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()
    return Campaign.objects.create(game=game, war=war, commander=commander)


def _upgrade_commander_to_statesman(campaign: Campaign, code: str, statesman_name: str, military: int = 5):
    commander = campaign.commander
    commander.code = code
    commander.statesman_name = statesman_name
    commander.military = military
    commander.save()


@pytest.mark.django_db
def test_scipio_nullifies_punic_war_disaster(basic_game: Game):
    # Arrange
    war = War.objects.create(
        game=basic_game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=10,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )
    campaign = _setup_combat(basic_game, war)
    _upgrade_commander_to_statesman(campaign, "1a", "P. Cornelius Scipio Africanus")
    for i in range(1, 11):
        Fleet.objects.create(game=basic_game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(basic_game.id, resolver)

    # Assert — disaster nullified; roll 13 + modifier 5 = 18, no losses
    assert Fleet.objects.filter(game=basic_game).count() == 10


@pytest.mark.django_db
def test_scipio_does_not_nullify_gallic_war_disaster(basic_game: Game):
    # Arrange
    war = War.objects.create(
        game=basic_game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )
    campaign = _setup_combat(basic_game, war)
    _upgrade_commander_to_statesman(campaign, "1a", "P. Cornelius Scipio Africanus")
    for i in range(1, 11):
        Legion.objects.create(game=basic_game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(basic_game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=basic_game).count() == 5


@pytest.mark.django_db
def test_flamininus_nullifies_macedonian_war_disaster(basic_game: Game):
    # Arrange
    war = War.objects.create(
        game=basic_game,
        name="1st Macedonian War",
        series_name="Macedonian",
        index=0,
        land_strength=7,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[],
        spoils=10,
        location="Macedonia",
        status=War.Status.ACTIVE,
    )
    campaign = _setup_combat(basic_game, war)
    _upgrade_commander_to_statesman(campaign, "18a", "T. Quinctius Flamininus")
    for i in range(1, 11):
        Legion.objects.create(game=basic_game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(basic_game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=basic_game).count() == 10


@pytest.mark.django_db
def test_fabius_halves_combat_losses(basic_game: Game):
    # Arrange
    war = War.objects.create(
        game=basic_game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )
    campaign = _setup_combat(basic_game, war)
    _upgrade_commander_to_statesman(campaign, "2a", "Q. Fabius Maximus Verrucosus Cunctator")
    for i in range(1, 11):
        Legion.objects.create(game=basic_game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(basic_game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=basic_game).count() == 8
