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
            JoinTheRevoltAction()
            if senator.family_name in joining
            else RemainLoyalAction()
        )
        assert senator.faction_id is not None
        action.execute(game.id, senator.faction_id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)


@pytest.mark.django_db
def test_veterans_owing_allegiance_to_the_primary_rebel_desert_from_the_reserve(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    game = campaign.game
    veteran = Legion.objects.create(
        game=game, number=3, veteran=True, allegiance=campaign.commander
    )
    _declare(campaign, resolver)

    # Act
    _decide(game, resolver)

    # Assert
    veteran.refresh_from_db()
    assert veteran.campaign == campaign


@pytest.mark.django_db
def test_veterans_owing_allegiance_to_a_secondary_rebel_desert(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    game = campaign.game
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    veteran = Legion.objects.create(
        game=game, number=3, veteran=True, allegiance=fabius
    )
    _declare(campaign, resolver)

    # Act
    _decide(game, resolver, joining=["Fabius"])

    # Assert
    veteran.refresh_from_db()
    assert veteran.campaign == campaign


@pytest.mark.django_db
def test_veterans_owing_allegiance_to_a_loyal_senator_stay_put(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    game = campaign.game
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    veteran = Legion.objects.create(
        game=game, number=3, veteran=True, allegiance=valerius
    )
    _declare(campaign, resolver)

    # Act
    _decide(game, resolver)

    # Assert
    veteran.refresh_from_db()
    assert veteran.campaign is None


@pytest.mark.django_db
def test_deserting_veterans_leave_a_senate_army(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    game = campaign.game
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
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    manlius.location = war.location
    manlius.save()
    senate_campaign = Campaign.objects.create(game=game, war=war, commander=manlius)
    veteran = Legion.objects.create(
        game=game,
        number=3,
        veteran=True,
        allegiance=campaign.commander,
        campaign=senate_campaign,
    )
    _declare(campaign, resolver)

    # Act
    _decide(game, resolver)

    # Assert
    veteran.refresh_from_db()
    assert veteran.campaign == campaign


@pytest.mark.django_db
def test_desertion_raises_the_civil_war_strength(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    game = campaign.game
    Legion.objects.create(
        game=game, number=3, veteran=True, allegiance=campaign.commander
    )
    _declare(campaign, resolver)

    # Act
    _decide(game, resolver)

    # Assert
    war = War.objects.get(game=game, primary_rebel__isnull=False)
    assert war.land_strength == 8
