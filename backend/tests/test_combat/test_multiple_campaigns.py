import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Faction, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.fixture
def two_campaigns(basic_game: Game):
    game = basic_game

    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.RESOLUTION
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

    commander1 = Senator.objects.get(game=game, name="Cornelius")
    commander1.add_title(Senator.Title.FIELD_CONSUL)
    commander1.location = war.location
    commander1.save()

    commander2 = Senator.objects.get(game=game, name="Julius")
    commander2.add_title(Senator.Title.ROME_CONSUL)
    commander2.location = war.location
    commander2.save()

    campaign1 = Campaign.objects.create(
        game=game, war=war, commander=commander1, imminent=True
    )
    campaign2 = Campaign.objects.create(
        game=game, war=war, commander=commander2, imminent=True
    )

    return (campaign1, campaign2)


@pytest.mark.django_db
def test_multiple_campaigns_commanders_agree(two_campaigns):

    # Arrange
    campaign1, campaign2 = two_campaigns
    game = campaign1.game
    commander1 = campaign1.commander
    commander2 = campaign2.commander
    assert commander1 is not None
    assert commander2 is not None

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign1)
    for i in range(11, 21):
        Legion.objects.create(game=game, number=i, campaign=campaign2)

    commander1.add_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
    commander1.save()

    faction1 = commander1.faction
    faction2 = commander2.faction
    assert faction1 is not None
    assert faction2 is not None
    faction1.add_status_item(StatusItem.DONE)
    faction1.save()
    faction2.add_status_item(StatusItem.DONE)
    faction2.save()

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [18, 18]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    assert Campaign.objects.filter(game=game).exists() == False
    commander1.refresh_from_db()
    assert commander1.alive == True
    assert commander1.location == "Rome"
    commander2.refresh_from_db()
    assert commander2.alive == True
    assert commander2.location == "Rome"


@pytest.mark.django_db
def test_multiple_campaigns_commanders_disagree(two_campaigns):

    # Arrange
    campaign1, campaign2 = two_campaigns
    game = campaign1.game
    commander1 = campaign1.commander
    commander2 = campaign2.commander
    assert commander1 is not None
    assert commander2 is not None

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign1)
    for i in range(11, 21):
        Legion.objects.create(game=game, number=i, campaign=campaign2)

    commander1.add_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
    commander1.save()
    commander2.add_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
    commander2.save()

    faction1 = commander1.faction
    faction2 = commander2.faction
    assert faction1 is not None
    assert faction2 is not None
    faction1.add_status_item(StatusItem.DONE)
    faction1.save()
    faction2.add_status_item(StatusItem.DONE)
    faction2.save()

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [18, 18]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    assert Campaign.objects.filter(game=game).exists() == False
    commander1.refresh_from_db()
    assert commander1.alive == True
    assert commander1.location == "Rome"
    commander2.refresh_from_db()
    assert commander2.alive == True
    assert commander2.location == "Rome"
