from typing import Callable

import pytest
from rorapp.actions.declare_civil_war import DeclareCivilWarAction
from rorapp.actions.join_the_revolt import JoinTheRevoltAction
from rorapp.actions.remain_loyal import RemainLoyalAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.civil_war import undecided_secondary_rebels
from rorapp.models import Campaign, Game, Legion, Senator, War


def _declare(campaign: Campaign, resolver: FakeRandomResolver) -> Game:
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction is not None
    DeclareCivilWarAction().execute(game.id, commander.faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)
    return game


def _decide(game: Game, resolver: FakeRandomResolver, joining=()) -> None:
    while True:
        undecided = undecided_secondary_rebels(game.id)
        if not undecided:
            break
        senator = undecided[0]
        action = (
            JoinTheRevoltAction() if senator.family_name in joining else RemainLoyalAction()
        )
        assert senator.faction_id is not None
        action.execute(game.id, senator.faction_id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)


@pytest.mark.django_db
def test_every_other_senator_in_the_faction_must_decide(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = _declare(land_victor, resolver)

    # Act
    undecided = undecided_secondary_rebels(game.id)

    # Assert
    assert sorted(s.family_name for s in undecided) == [
        "Fabius",
        "Julius",
        "Valerius",
    ]


@pytest.mark.django_db
def test_a_senator_who_joins_becomes_a_rebel(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = _declare(land_victor, resolver)

    # Act
    _decide(game, resolver, joining=["Fabius"])

    # Assert
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    assert fabius.rebel == True
    assert fabius.location == "Italia"
    assert valerius.rebel == False
    assert valerius.location == "Rome"


@pytest.mark.django_db
def test_a_master_of_horse_may_not_join_a_rebel_who_is_not_a_dictator(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2, 3])
    master_of_horse = Senator.objects.get(game=campaign.game, family_name="Fabius")
    master_of_horse.add_title(Senator.Title.MASTER_OF_HORSE)
    master_of_horse.save()
    game = _declare(campaign, resolver)

    # Act
    assert master_of_horse.faction_id is not None
    result = JoinTheRevoltAction().execute(
        game.id, master_of_horse.faction_id, {}, resolver
    )

    # Assert
    assert result.success == False
    master_of_horse.refresh_from_db()
    assert master_of_horse.rebel == False


@pytest.mark.django_db
def test_a_master_of_horse_may_join_a_rebel_dictator(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor(
        "Cornelius", [1, 2, 3], master_of_horse_name="Fabius"
    )
    dictator = campaign.commander
    assert dictator is not None
    dictator.add_title(Senator.Title.DICTATOR)
    dictator.save()
    game = _declare(campaign, resolver)

    # Act
    _decide(game, resolver, joining=["Fabius"])

    # Assert
    master_of_horse = Senator.objects.get(game=game, family_name="Fabius")
    assert master_of_horse.rebel == True
    assert master_of_horse.location == "Italia"


@pytest.mark.django_db
def test_a_master_of_horse_who_stays_loyal_returns_to_rome_with_his_office(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor(
        "Cornelius", [1, 2, 3], master_of_horse_name="Fabius"
    )
    dictator = campaign.commander
    assert dictator is not None
    dictator.add_title(Senator.Title.DICTATOR)
    dictator.save()
    game = _declare(campaign, resolver)

    # Act
    _decide(game, resolver)

    # Assert
    master_of_horse = Senator.objects.get(game=game, family_name="Fabius")
    assert master_of_horse.location == "Rome"
    assert master_of_horse.has_title(Senator.Title.MASTER_OF_HORSE)
    campaign.refresh_from_db()
    assert campaign.master_of_horse is None


@pytest.mark.django_db
def test_a_consul_for_life_is_never_asked_to_join(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    consul_for_life = Senator.objects.get(game=land_victor.game, family_name="Fabius")
    consul_for_life.add_title(Senator.Title.CONSUL_FOR_LIFE)
    consul_for_life.save()

    # Act
    game = _declare(land_victor, resolver)

    # Assert
    undecided = undecided_secondary_rebels(game.id)
    assert "Fabius" not in [s.family_name for s in undecided]


@pytest.mark.django_db
def test_a_consul_for_life_may_not_declare_civil_war(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2, 3])
    commander = campaign.commander
    assert commander is not None
    commander.add_title(Senator.Title.CONSUL_FOR_LIFE)
    commander.save()

    # Act
    game = _declare(campaign, resolver)

    # Assert
    assert War.objects.filter(game=game, primary_rebel__isnull=False).exists() == False


@pytest.mark.django_db
def test_a_secondary_rebel_leaves_his_forces_to_the_senate(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    rebel = add_land_victor("Cornelius", [1, 2, 3])
    game = rebel.game
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
    proconsul = Senator.objects.get(game=game, family_name="Fabius")
    proconsul.add_title(Senator.Title.PROCONSUL)
    proconsul.location = war.location
    proconsul.save()
    proconsul_campaign = Campaign.objects.create(
        game=game, war=war, commander=proconsul
    )
    for number in [4, 5]:
        Legion.objects.create(game=game, number=number, campaign=proconsul_campaign)
    _declare(rebel, resolver)

    # Act
    _decide(game, resolver, joining=["Fabius"])

    # Assert
    proconsul.refresh_from_db()
    assert proconsul.rebel == True
    proconsul_campaign.refresh_from_db()
    assert proconsul_campaign.commander is None
    assert Legion.objects.filter(game=game, campaign=proconsul_campaign).count() == 2
    assert Legion.objects.filter(game=game, campaign=rebel).count() == 3
