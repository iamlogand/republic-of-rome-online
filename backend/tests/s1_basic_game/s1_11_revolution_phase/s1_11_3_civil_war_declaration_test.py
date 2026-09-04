from typing import Callable

import pytest
from rorapp.actions.declare_civil_war import DeclareCivilWarAction
from rorapp.actions.lay_down_command import LayDownCommandAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Fleet, Game, Log, Senator, War


def _declare(campaign: Campaign, resolver: FakeRandomResolver):
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction is not None
    return DeclareCivilWarAction().execute(
        game.id, commander.faction.id, {}, resolver
    )


@pytest.mark.django_db
def test_declaration_creates_an_active_civil_war(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game

    # Act
    _declare(land_victor, resolver)

    # Assert
    war = War.objects.get(game=game, primary_rebel__isnull=False)
    assert war.name == "Civil War"
    assert war.status == War.Status.ACTIVE
    assert war.location == "Italia"
    assert war.primary_rebel == land_victor.commander
    assert war.spoils == 0
    assert war.fleet_support == 0
    assert war.naval_strength == 0


@pytest.mark.django_db
def test_civil_war_strength_caps_the_military_rating_at_the_army(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])

    # Act
    _declare(campaign, resolver)

    # Assert
    war = War.objects.get(game=campaign.game, primary_rebel__isnull=False)
    assert war.land_strength == 4


@pytest.mark.django_db
def test_civil_war_strength_adds_the_full_military_rating_to_a_large_army(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game

    # Act
    _declare(land_victor, resolver)

    # Assert
    war = War.objects.get(game=game, primary_rebel__isnull=False)
    assert war.land_strength == 9


@pytest.mark.django_db
def test_rebel_marches_on_rome(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None

    # Act
    _declare(land_victor, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.rebel == True
    assert commander.location == "Italia"


@pytest.mark.django_db
def test_fleets_return_to_the_reserve(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2, 3], fleet_numbers=[1, 2])

    # Act
    _declare(campaign, resolver)

    # Assert
    assert Fleet.objects.filter(game=campaign.game, campaign__isnull=False).count() == 0
    assert Fleet.objects.filter(game=campaign.game).count() == 2


@pytest.mark.django_db
def test_declaration_is_logged(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game

    # Act
    _declare(land_victor, resolver)

    # Assert
    assert Log.objects.filter(
        game=game,
        text="Cornelius declared himself in revolt and is marching on Rome "
        "with 5 legions (I–V).",
    ).exists()


@pytest.mark.django_db
def test_stronger_army_displaces_the_standing_rebel(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    weaker = add_land_victor("Cornelius", [1, 2, 3, 4, 5])
    stronger = add_land_victor("Manlius", [6, 7, 8, 9, 10, 11, 12])
    _declare(weaker, resolver)

    # Act
    _declare(stronger, resolver)

    # Assert
    wars = War.objects.filter(game=weaker.game, primary_rebel__isnull=False)
    assert wars.count() == 1
    assert wars.first().primary_rebel == stronger.commander
    displaced = Senator.objects.get(game=weaker.game, family_name="Cornelius")
    assert displaced.rebel == False
    assert displaced.location == "Rome"
    assert not Campaign.objects.filter(id=weaker.id).exists()


@pytest.mark.django_db
def test_weaker_army_may_not_declare(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    stronger = add_land_victor("Cornelius", [1, 2, 3, 4, 5])
    weaker = add_land_victor("Manlius", [6, 7, 8, 9, 10])
    _declare(stronger, resolver)

    # Act
    result = _declare(weaker, resolver)

    # Assert
    assert result.success == False
    war = War.objects.get(game=weaker.game, primary_rebel__isnull=False)
    assert war.primary_rebel == stronger.commander


@pytest.mark.django_db
def test_second_victor_in_the_rebel_faction_may_not_declare(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    rebel = add_land_victor("Cornelius", [1, 2, 3])
    factionmate = add_land_victor("Fabius", [4, 5, 6, 7, 8, 9])
    _declare(rebel, resolver)

    # Act
    result = _declare(factionmate, resolver)

    # Assert
    assert result.success == False
    war = War.objects.get(game=rebel.game, primary_rebel__isnull=False)
    assert war.primary_rebel == rebel.commander


@pytest.mark.django_db
def test_declaration_order_starts_with_the_highest_ranking_senators_faction(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    second = add_land_victor("Manlius", [1, 2, 3])
    first = add_land_victor("Cornelius", [4, 5, 6])
    game = first.game

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    second_faction = game.factions.get(position=2)
    result = DeclareCivilWarAction().execute(game.id, second_faction.id, {}, resolver)
    assert result.success == False
    assert War.objects.filter(game=game, primary_rebel__isnull=False).exists() == False


@pytest.mark.django_db
def test_revolution_ends_once_every_victor_has_decided(
    add_land_victor: Callable[..., Campaign],
    settle_secondary_rebels: Callable[[Game], None],
    resolver: FakeRandomResolver,
):
    # Arrange
    rebel = add_land_victor("Cornelius", [1, 2, 3])
    loyal = add_land_victor("Manlius", [4, 5, 6])
    game = rebel.game
    _declare(rebel, resolver)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)
    manlius = loyal.commander
    assert manlius is not None and manlius.faction is not None
    LayDownCommandAction().execute(game.id, manlius.faction.id, {}, resolver)
    settle_secondary_rebels(game)

    # Assert
    game.refresh_from_db()
    assert game.phase != Game.Phase.REVOLUTION
    assert game.turn == 2


@pytest.mark.django_db
def test_a_standing_rebel_from_an_earlier_turn_may_not_be_displaced(
    add_land_victor: Callable[..., Campaign],
    settle_secondary_rebels: Callable[[Game], None],
    resolver: FakeRandomResolver,
):
    # Arrange
    rebel = add_land_victor("Cornelius", [1, 2, 3])
    game = rebel.game
    _declare(rebel, resolver)
    settle_secondary_rebels(game)
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.CIVIL_WAR_DECLARATION
    game.save()
    challenger = add_land_victor("Manlius", [4, 5, 6, 7, 8, 9, 10])

    # Act
    result = _declare(challenger, resolver)

    # Assert
    assert result.success == False
    war = War.objects.get(game=game, primary_rebel__isnull=False)
    assert war.primary_rebel == rebel.commander


@pytest.mark.django_db
def test_the_rebel_hands_the_hrao_title_to_a_senator_in_rome(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    commander.add_title(Senator.Title.HRAO)
    commander.save()

    # Act
    _declare(land_victor, resolver)

    # Assert
    commander.refresh_from_db()
    assert not commander.has_title(Senator.Title.HRAO)
    hrao = Senator.objects.get(game=land_victor.game, titles__contains=["HRAO"])
    assert hrao.location == "Rome"
