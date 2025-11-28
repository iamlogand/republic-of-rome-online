import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Game, Fleet, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.fixture
def naval_campaign(basic_game: Game):
    game = basic_game

    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.unrest = 3
    game.save()

    war = War.objects.create(
        game=game,
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

    commander = Senator.objects.get(game=game, name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()

    campaign = Campaign.objects.create(game=game, war=war, commander=commander)

    return campaign


@pytest.mark.django_db
def test_naval_battle_victory(naval_campaign: Campaign):

    campaign = naval_campaign
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [18]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_fleet_count = Fleet.objects.filter(game=game).count()
    assert surviving_fleet_count == 10
    game.refresh_from_db()
    assert game.unrest == 2
    commander.refresh_from_db()
    assert commander.alive == True
    assert commander.popularity == 5
    assert commander.location == "Sicilia"
    assert Campaign.objects.filter(game=game).exists() == True
    campaign.refresh_from_db()
    assert campaign.commander == commander


@pytest.mark.django_db
def test_naval_battle_stalemate(naval_campaign: Campaign):

    campaign = naval_campaign
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [7]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_fleet_count = Fleet.objects.filter(game=game).count()
    assert surviving_fleet_count == 8
    game.refresh_from_db()
    assert game.unrest == 3
    commander.refresh_from_db()
    assert commander.alive == True
    assert commander.popularity == 0
    assert commander.location == "Sicilia"
    assert Campaign.objects.filter(game=game).exists() == True
    campaign.refresh_from_db()
    assert campaign.commander == commander


@pytest.mark.django_db
def test_naval_battle_defeat(naval_campaign: Campaign):

    campaign = naval_campaign
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [3]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_fleet_count = Fleet.objects.filter(game=game).count()
    assert surviving_fleet_count == 9
    game.refresh_from_db()
    assert game.unrest == 5
    commander.refresh_from_db()
    assert commander.alive == False


@pytest.mark.django_db
def test_naval_battle_total_defeat(naval_campaign: Campaign):

    campaign = naval_campaign
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None

    for i in range(1, 6):
        Fleet.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [1]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_fleet_count = Fleet.objects.filter(game=game).count()
    assert surviving_fleet_count == 0
    game.refresh_from_db()
    assert game.unrest == 5
    commander.refresh_from_db()
    assert commander.alive == False
    assert Campaign.objects.filter(game=game).exists() == False


@pytest.mark.django_db
def test_naval_battle_standoff(naval_campaign: Campaign):

    campaign = naval_campaign
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [11]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_fleet_count = Fleet.objects.filter(game=game).count()
    assert surviving_fleet_count == 7
    game.refresh_from_db()
    assert game.unrest == 3
    commander.refresh_from_db()
    assert commander.alive == True
    assert commander.popularity == 0
    assert commander.location == "Sicilia"
    assert Campaign.objects.filter(game=game).exists() == True
    campaign.refresh_from_db()
    assert campaign.commander == commander


@pytest.mark.django_db
def test_naval_battle_disaster(naval_campaign: Campaign):

    campaign = naval_campaign
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [13]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_fleet_count = Fleet.objects.filter(game=game).count()
    assert surviving_fleet_count == 5
    game.refresh_from_db()
    assert game.unrest == 4
    commander.refresh_from_db()
    assert commander.alive == True
    assert commander.popularity == 0
    assert commander.location == "Sicilia"
    assert Campaign.objects.filter(game=game).exists() == True
    campaign.refresh_from_db()
    assert campaign.commander == commander
