from typing import Callable

import pytest
from rorapp.actions.declare_revolt import DeclareRevoltAction
from rorapp.actions.lay_down_command import LayDownCommandAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.effects.revolt_declaration_next import RevoltDeclarationNextEffect
from rorapp.effects.revolution_phase_end import RevolutionPhaseEndEffect
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Faction, Fleet, Game, Log, Senator, War

pytestmark = pytest.mark.usefixtures("civil_war_flag")


def _declare(campaign: Campaign, resolver: FakeRandomResolver) -> None:
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction_id is not None
    DeclareRevoltAction().execute(game.id, commander.faction_id, {}, resolver)


def _declaration_offered(campaign: Campaign, resolver: FakeRandomResolver) -> bool:
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction_id is not None
    faction = DeclareRevoltAction().is_allowed(
        GameStateSnapshot(game.id), commander.faction_id
    )
    return faction is not None


def _factions_awaiting_decision(game: Game) -> list[int]:
    return [
        f.id
        for f in Faction.objects.filter(game=game)
        if f.has_status_item(FactionStatusItem.AWAITING_DECISION)
    ]


@pytest.mark.django_db
def test_declaration_creates_an_active_revolt(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game

    # Act
    _declare(land_victor, resolver)

    # Assert
    war = War.objects.get(game=game, primary_rebel__isnull=False)
    assert war.name == "Revolt"
    assert war.status == War.Status.ACTIVE
    assert war.location == "Italia"
    assert war.primary_rebel == land_victor.commander
    assert war.spoils == 0
    assert war.fleet_support == 0
    assert war.naval_strength == 0


@pytest.mark.django_db
def test_revolt_strength_caps_the_military_rating_at_the_army(
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
def test_revolt_strength_adds_the_full_military_rating_to_a_large_army(
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
    execute_effects_and_manage_actions(land_victor.game.id, resolver)

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
    execute_effects_and_manage_actions(campaign.game.id, resolver)

    # Assert
    assert Fleet.objects.filter(game=campaign.game, campaign__isnull=False).count() == 0
    assert Fleet.objects.filter(game=campaign.game).count() == 2


@pytest.mark.django_db
def test_master_of_horse_returns_to_rome_and_keeps_his_office(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2, 3], master_of_horse_name="Fabius")

    # Act
    _declare(campaign, resolver)
    execute_effects_and_manage_actions(campaign.game.id, resolver)

    # Assert
    master_of_horse = Senator.objects.get(game=campaign.game, family_name="Fabius")
    assert master_of_horse.location == "Rome"
    assert master_of_horse.has_title(Senator.Title.MASTER_OF_HORSE)
    campaign.refresh_from_db()
    assert campaign.master_of_horse is None
    assert Log.objects.filter(
        game=campaign.game,
        text="Cornelius marched on Rome. Fabius returned to Rome.",
    ).exists()


@pytest.mark.django_db
def test_returning_master_of_horse_takes_the_hrao(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2, 3], master_of_horse_name="Fabius")
    hrao = Senator.objects.get(game=campaign.game, family_name="Valerius")
    hrao.add_title(Senator.Title.HRAO)
    hrao.save()

    # Act
    _declare(campaign, resolver)
    execute_effects_and_manage_actions(campaign.game.id, resolver)

    # Assert
    master_of_horse = Senator.objects.get(game=campaign.game, family_name="Fabius")
    assert master_of_horse.has_title(Senator.Title.HRAO)
    hrao.refresh_from_db()
    assert not hrao.has_title(Senator.Title.HRAO)


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
        text="Cornelius declared himself in revolt with 5 legions (I–V).",
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
    assert wars.get().primary_rebel == stronger.commander
    displaced = Senator.objects.get(game=weaker.game, family_name="Cornelius")
    assert displaced.rebel == False
    assert displaced.location == "Rome"
    assert not Campaign.objects.filter(id=weaker.id).exists()


@pytest.mark.django_db
def test_displaced_rebel_takes_his_whole_force_home(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    weaker = add_land_victor(
        "Cornelius",
        [1, 2, 3, 4, 5],
        fleet_numbers=[1, 2],
        master_of_horse_name="Fabius",
    )
    stronger = add_land_victor("Manlius", [6, 7, 8, 9, 10, 11, 12])
    _declare(weaker, resolver)

    # Act
    _declare(stronger, resolver)

    # Assert
    assert Fleet.objects.filter(game=weaker.game, campaign__isnull=False).count() == 0
    master_of_horse = Senator.objects.get(game=weaker.game, family_name="Fabius")
    assert master_of_horse.location == "Rome"
    assert Log.objects.filter(
        game=weaker.game,
        text="Cornelius and Fabius returned to Rome. "
        "5 legions (I–V) and 2 fleets (I and II) returned to the reserve forces.",
    ).exists()


@pytest.mark.django_db
def test_rebel_loses_his_offices_once_the_declarations_end(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.add_title(Senator.Title.PROCONSUL)
    commander.save()

    # Act
    _declare(land_victor, resolver)
    execute_effects_and_manage_actions(land_victor.game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert not commander.has_title(Senator.Title.FIELD_CONSUL)
    assert not commander.has_title(Senator.Title.PROCONSUL)


@pytest.mark.django_db
def test_displaced_rebel_keeps_his_offices(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    weaker = add_land_victor("Cornelius", [1, 2, 3, 4, 5])
    stronger = add_land_victor("Manlius", [6, 7, 8, 9, 10, 11, 12])
    displaced = weaker.commander
    assert displaced is not None
    displaced.add_title(Senator.Title.FIELD_CONSUL)
    displaced.save()
    _declare(weaker, resolver)

    # Act
    _declare(stronger, resolver)
    execute_effects_and_manage_actions(weaker.game.id, resolver)

    # Assert
    displaced.refresh_from_db()
    assert displaced.has_title(Senator.Title.FIELD_CONSUL)


@pytest.mark.django_db
def test_weaker_army_may_not_declare(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    stronger = add_land_victor("Cornelius", [1, 2, 3, 4, 5])
    weaker = add_land_victor("Manlius", [6, 7, 8, 9, 10])
    _declare(stronger, resolver)

    # Act
    offered = _declaration_offered(weaker, resolver)

    # Assert
    assert offered == False


@pytest.mark.django_db
def test_second_victor_in_the_rebel_faction_may_not_declare(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    rebel = add_land_victor("Cornelius", [1, 2, 3])
    factionmate = add_land_victor("Fabius", [4, 5, 6, 7, 8, 9])
    _declare(rebel, resolver)

    # Act
    offered = _declaration_offered(factionmate, resolver)

    # Assert
    assert offered == False


@pytest.mark.django_db
def test_declaration_order_starts_with_the_hraos_faction(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    first = add_land_victor("Manlius", [1, 2, 3])
    later = add_land_victor("Cornelius", [4, 5, 6])
    hrao = Senator.objects.get(game=later.game, family_name="Claudius")
    hrao.add_title(Senator.Title.HRAO)
    hrao.save()

    # Act
    first_offered = _declaration_offered(first, resolver)
    later_offered = _declaration_offered(later, resolver)

    # Assert
    assert first_offered == True
    assert later_offered == False


@pytest.mark.django_db
def test_declaration_is_not_offered_with_the_flag_off(
    land_victor: Campaign, settings
):
    # Arrange
    game = land_victor.game
    game.sub_phase = Game.SubPhase.REVOLT_DECLARATION
    game.save()
    commander = land_victor.commander
    assert commander is not None and commander.faction is not None
    commander.faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    commander.faction.save()
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "civil_war": False}

    # Act
    faction = DeclareRevoltAction().is_allowed(
        GameStateSnapshot(game.id), commander.faction.id
    )

    # Assert
    assert faction is None


@pytest.mark.django_db
def test_no_faction_is_asked_to_decide_with_the_flag_off(
    land_victor: Campaign, settings
):
    # Arrange
    game = land_victor.game
    game.sub_phase = Game.SubPhase.REVOLT_DECLARATION
    game.save()
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "civil_war": False}

    # Act
    valid = RevoltDeclarationNextEffect().validate(GameStateSnapshot(game.id))

    # Assert
    assert valid == False


@pytest.mark.django_db
def test_revolution_ends_once_every_victor_has_decided(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
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
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase != Game.Phase.REVOLUTION
    assert game.turn == 2


@pytest.mark.django_db
def test_a_standing_rebel_from_an_earlier_turn_may_not_be_displaced(
    add_land_victor: Callable[..., Campaign],
    resolver: FakeRandomResolver,
):
    # Arrange
    rebel = add_land_victor("Cornelius", [1, 2, 3])
    game = rebel.game
    _declare(rebel, resolver)
    RevolutionPhaseEndEffect().execute(game.id, resolver)
    game.refresh_from_db()
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.REVOLT_DECLARATION
    game.save()
    challenger = add_land_victor("Manlius", [4, 5, 6, 7, 8, 9, 10])

    # Act
    offered = _declaration_offered(challenger, resolver)

    # Assert
    assert offered == False


@pytest.mark.django_db
def test_displaced_rebel_regains_the_hrao(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    weaker = add_land_victor("Cornelius", [1, 2, 3, 4, 5])
    stronger = add_land_victor("Manlius", [6, 7, 8, 9, 10, 11, 12])
    displaced = weaker.commander
    assert displaced is not None
    displaced.add_title(Senator.Title.DICTATOR)
    displaced.save()
    consul = Senator.objects.get(game=weaker.game, family_name="Fabius")
    consul.add_title(Senator.Title.ROME_CONSUL)
    consul.add_title(Senator.Title.HRAO)
    consul.save()
    _declare(weaker, resolver)

    # Act
    _declare(stronger, resolver)

    # Assert
    displaced.refresh_from_db()
    assert displaced.has_title(Senator.Title.HRAO)
    consul.refresh_from_db()
    assert not consul.has_title(Senator.Title.HRAO)


@pytest.mark.django_db
def test_each_victor_decides_in_turn(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    first = add_land_victor("Cornelius", [1, 2, 3])
    second = add_land_victor("Manlius", [4, 5, 6])
    game = first.game

    # Act
    execute_effects_and_manage_actions(game.id, resolver)
    awaiting_before = _factions_awaiting_decision(game)
    _declare(first, resolver)
    execute_effects_and_manage_actions(game.id, resolver)
    awaiting_after = _factions_awaiting_decision(game)

    # Assert
    assert first.commander is not None and second.commander is not None
    assert awaiting_before == [first.commander.faction_id]
    assert awaiting_after == [second.commander.faction_id]
