import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.fixture
def land_campaign(basic_game: Game):
    game = basic_game

    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.unrest = 3
    game.save()

    war = War.objects.create(
        game=game,
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

    commander = Senator.objects.get(game=game, name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()

    campaign = Campaign.objects.create(game=game, war=war, commander=commander)

    return campaign


@pytest.mark.django_db
def test_land_battle_victory(land_campaign: Campaign):

    campaign = land_campaign
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [18]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_legion_count = Legion.objects.filter(game=game).count()
    assert surviving_legion_count == 10
    game.refresh_from_db()
    assert game.unrest == 2
    commander.refresh_from_db()
    assert commander.alive == True
    assert commander.popularity == 5
    assert commander.location == "Rome"
    assert Campaign.objects.filter(game=game).exists() == False


@pytest.mark.django_db
def test_land_battle_stalemate(land_campaign: Campaign):

    campaign = land_campaign
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [5]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_legion_count = Legion.objects.filter(game=game).count()
    assert surviving_legion_count == 6
    game.refresh_from_db()
    assert game.unrest == 3
    commander.refresh_from_db()
    assert commander.alive == True
    assert commander.popularity == -2
    assert Campaign.objects.filter(game=game).exists() == True
    campaign.refresh_from_db()
    assert campaign.commander == commander


@pytest.mark.django_db
def test_land_battle_defeat(land_campaign: Campaign):

    campaign = land_campaign
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None

    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [4]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_legion_count = Legion.objects.filter(game=game).count()
    assert surviving_legion_count == 2
    game.refresh_from_db()
    assert game.unrest == 5
    commander.refresh_from_db()
    assert commander.alive == False
    assert Campaign.objects.filter(game=game).exists() == True
    campaign.refresh_from_db()
    assert campaign.commander == None


@pytest.mark.django_db
def test_land_battle_defeat_total(land_campaign: Campaign):

    campaign = land_campaign
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None

    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [3]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_legion_count = Legion.objects.filter(game=game).count()
    assert surviving_legion_count == 0
    game.refresh_from_db()
    assert game.unrest == 5
    commander.refresh_from_db()
    assert commander.alive == False
    assert Campaign.objects.filter(game=game).exists() == False


@pytest.mark.django_db
def test_land_battle_standoff(land_campaign: Campaign):

    campaign = land_campaign
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [15]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_legion_count = Legion.objects.filter(game=game).count()
    assert surviving_legion_count == 7
    game.refresh_from_db()
    assert game.unrest == 3
    commander.refresh_from_db()
    assert commander.alive == True
    assert commander.popularity == -1
    assert commander.location == "Cisalpine Gaul"
    assert Campaign.objects.filter(game=game).exists() == True
    campaign.refresh_from_db()
    assert campaign.commander == commander


@pytest.mark.django_db
def test_land_battle_disaster(land_campaign: Campaign):

    campaign = land_campaign
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [13]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    surviving_legion_count = Legion.objects.filter(game=game).count()
    assert surviving_legion_count == 5
    game.refresh_from_db()
    assert game.unrest == 4
    commander.refresh_from_db()
    assert commander.alive == True
    assert commander.popularity == -2
    assert commander.location == "Cisalpine Gaul"
    assert Campaign.objects.filter(game=game).exists() == True
    campaign.refresh_from_db()
    assert campaign.commander == commander
