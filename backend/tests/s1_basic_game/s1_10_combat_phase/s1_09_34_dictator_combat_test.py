import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War


# Valerius: mil=1, code="3"  MoH Furius: mil=3, code="8"  combined=4
# War land_strength=8, 3 legions, roll=10:
#   with MoH:    effective=min(4,3)=3, modifier=3+3-8=-2, modified=8  → stalemate (8>=8, <14)
#   without MoH: effective=min(1,3)=1, modifier=3+1-8=-4, modified=6  → defeat   (6<8)
@pytest.fixture
def dictator_land_campaign(basic_game: Game):
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
        land_strength=8,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )

    dictator = Senator.objects.get(game=game, family_name="Valerius")
    dictator.add_title(Senator.Title.DICTATOR)
    dictator.location = war.location
    dictator.save()

    moh = Senator.objects.get(game=game, family_name="Furius")
    moh.add_title(Senator.Title.MASTER_OF_HORSE)
    moh.location = war.location
    moh.save()

    return Campaign.objects.create(game=game, war=war, commander=dictator, master_of_horse=moh)


# Cornelius: mil=4, code="1"  MoH Claudius: mil=2, code="5"  combined=6
# War land_strength=6, 8 legions, roll=18:
#   effective=min(6,8)=6, modifier=8+6-6=8, modified=26  → victory, no losses
#   glory=(6+1)//2=3  → dictator gains 3 influence and 3 popularity
@pytest.fixture
def dictator_victory_campaign(basic_game: Game):
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
        land_strength=6,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )

    dictator = Senator.objects.get(game=game, family_name="Cornelius")
    dictator.add_title(Senator.Title.DICTATOR)
    dictator.location = war.location
    dictator.save()

    moh = Senator.objects.get(game=game, family_name="Claudius")
    moh.add_title(Senator.Title.MASTER_OF_HORSE)
    moh.location = war.location
    moh.save()

    for i in range(1, 9):
        Legion.objects.create(game=game, number=i, campaign=None)

    campaign = Campaign.objects.create(game=game, war=war, commander=dictator, master_of_horse=moh)
    for legion in Legion.objects.filter(game=game):
        legion.campaign = campaign
        legion.save()
    return campaign


@pytest.mark.django_db
def test_dictator_moh_military_combined_in_land_battle(dictator_land_campaign: Campaign):
    # Arrange
    game = dictator_land_campaign.game
    dictator = dictator_land_campaign.commander
    for i in range(1, 4):
        Legion.objects.create(game=game, number=i, campaign=dictator_land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [10]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert — stalemate (not defeat), so dictator survives
    assert dictator is not None
    assert Senator.objects.filter(id=dictator.id).exists()
    dictator.refresh_from_db()
    assert dictator.alive


@pytest.mark.django_db
def test_dictator_moh_military_combined_in_naval_battle(basic_game: Game):
    # Arrange
    # Valerius (mil=1) + Furius (mil=3) = combined 4
    # naval_strength=8, 3 fleets, roll=10:
    #   with MoH:    effective=min(4,3)=3, modifier=3+3-8=-2, modified=8  → stalemate
    #   without MoH: effective=min(1,3)=1, modifier=3+1-8=-4, modified=6  → defeat
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
        fleet_support=3,
        naval_strength=8,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )
    dictator = Senator.objects.get(game=game, family_name="Valerius")
    dictator.add_title(Senator.Title.DICTATOR)
    dictator.location = war.location
    dictator.save()
    moh = Senator.objects.get(game=game, family_name="Furius")
    moh.add_title(Senator.Title.MASTER_OF_HORSE)
    moh.location = war.location
    moh.save()
    campaign = Campaign.objects.create(game=game, war=war, commander=dictator, master_of_horse=moh)
    for i in range(1, 4):
        Fleet.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [10]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert — stalemate (not defeat), so dictator survives
    assert Senator.objects.filter(id=dictator.id).exists()
    dictator.refresh_from_db()
    assert dictator.alive


@pytest.mark.django_db
def test_dictator_victory_dictator_gains_influence_and_popularity(dictator_victory_campaign: Campaign):
    # Arrange
    game = dictator_victory_campaign.game
    dictator = dictator_victory_campaign.commander
    assert dictator is not None
    initial_influence = dictator.influence
    initial_popularity = dictator.popularity
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert — glory = (6+1)//2 = 3
    dictator.refresh_from_db()
    assert dictator.influence == initial_influence + 3
    assert dictator.popularity == initial_popularity + 3


@pytest.mark.django_db
def test_dictator_victory_moh_gets_nothing(dictator_victory_campaign: Campaign):
    # Arrange
    game = dictator_victory_campaign.game
    moh = dictator_victory_campaign.master_of_horse
    assert moh is not None
    initial_influence = moh.influence
    initial_popularity = moh.popularity
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    moh.refresh_from_db()
    assert moh.influence == initial_influence
    assert moh.popularity == initial_popularity


@pytest.mark.django_db
def test_moh_killed_on_defeat(dictator_land_campaign: Campaign):
    # Arrange
    # Valerius (mil=1) + Furius (mil=3) combined=4, land_strength=10, 5 legions, roll=4:
    #   effective=min(4,5)=4, modifier=5+4-10=-1, modified=3  → defeat
    game = dictator_land_campaign.game
    dictator_land_campaign.war.land_strength = 10
    dictator_land_campaign.war.save()
    moh = dictator_land_campaign.master_of_horse
    assert moh is not None
    moh_id = moh.id
    for i in range(1, 6):
        Legion.objects.create(game=game, number=i, campaign=dictator_land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [4]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert — defeat kills both commander and MoH
    moh = Senator.objects.get(id=moh_id)
    assert not moh.alive


@pytest.mark.django_db
def test_moh_survives_disaster_independently(dictator_land_campaign: Campaign):
    # Arrange
    # Roll=13 → disaster; mortality chit "3" (Valerius) kills dictator; Furius (code "8") survives
    game = dictator_land_campaign.game
    moh = dictator_land_campaign.master_of_horse
    assert moh is not None
    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=dictator_land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]
    resolver.casualty_order = []
    resolver.mortality_chits = ["3"]  # Valerius code — dictator dies, MoH survives

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    moh.refresh_from_db()
    assert moh.alive


@pytest.mark.django_db
def test_dictator_killed_moh_returns_to_rome(dictator_land_campaign: Campaign):
    # Arrange
    game = dictator_land_campaign.game
    moh = dictator_land_campaign.master_of_horse
    assert moh is not None
    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=dictator_land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]
    resolver.casualty_order = []
    resolver.mortality_chits = ["3"]  # Valerius code — dictator dies, MoH survives

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    moh.refresh_from_db()
    assert moh.location == "Rome"


@pytest.mark.django_db
def test_dictator_killed_moh_keeps_title(dictator_land_campaign: Campaign):
    # Arrange
    game = dictator_land_campaign.game
    moh = dictator_land_campaign.master_of_horse
    assert moh is not None
    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=dictator_land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]
    resolver.casualty_order = []
    resolver.mortality_chits = ["3"]  # Valerius code — dictator dies, MoH survives

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    moh.refresh_from_db()
    assert moh.has_title(Senator.Title.MASTER_OF_HORSE)
