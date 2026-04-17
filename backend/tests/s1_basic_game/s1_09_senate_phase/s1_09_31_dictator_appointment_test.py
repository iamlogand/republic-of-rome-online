import pytest
from rorapp.actions.appoint_dictator import AppointDictatorAction
from rorapp.actions.skip import SkipAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.dictator_appointment import appoint_dictator
from rorapp.helpers.transfer_power_consuls import transfer_power_consuls
from rorapp.models import Game, Senator, War


def _make_active_war(game: Game, name: str, land: int = 5, naval: int = 0) -> War:
    return War.objects.create(
        game=game,
        name=name,
        series_name=name,
        index=0,
        land_strength=land,
        fleet_support=0,
        naval_strength=naval,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Somewhere",
        status=War.Status.ACTIVE,
    )


def _setup_appointment_game(game: Game) -> Game:
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.DICTATOR_APPOINTMENT
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    cornelius.add_title(Senator.Title.ROME_CONSUL)
    cornelius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    cornelius.add_title(Senator.Title.HRAO)
    cornelius.save()
    return game


@pytest.mark.django_db
def test_military_crisis_triggers_dictator_appointment_subphase(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    for i in range(1, 4):
        _make_active_war(game, f"War {i}")
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")

    # Act
    transfer_power_consuls(game.id, cornelius.id, claudius.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.DICTATOR_APPOINTMENT


@pytest.mark.django_db
def test_no_military_crisis_skips_dictator_appointment(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    _make_active_war(game, "Small War", land=5, naval=0)
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")

    # Act
    transfer_power_consuls(game.id, cornelius.id, claudius.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.CENSOR_ELECTION


@pytest.mark.django_db
def test_military_crisis_single_war_strength_20(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    _make_active_war(game, "Massive War", land=15, naval=5)
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")

    # Act
    transfer_power_consuls(game.id, cornelius.id, claudius.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.DICTATOR_APPOINTMENT


@pytest.mark.django_db
def test_both_consuls_same_faction_appoints_dictator_immediately(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = _setup_appointment_game(basic_game)
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    fabius.add_title(Senator.Title.FIELD_CONSUL)
    fabius.save()
    julius = Senator.objects.get(game=game, family_name="Julius")
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    faction_0 = cornelius.faction
    assert faction_0 is not None

    # Act
    AppointDictatorAction().execute(game.id, faction_0.id, {"Dictator": julius.id}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    julius.refresh_from_db()
    assert julius.has_title(Senator.Title.DICTATOR)


@pytest.mark.django_db
def test_both_consul_factions_agree_appoints_dictator(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = _setup_appointment_game(basic_game)
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.add_title(Senator.Title.FIELD_CONSUL)
    claudius.save()
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    faction_0 = cornelius.faction
    faction_1 = claudius.faction
    assert faction_0 is not None
    assert faction_1 is not None

    # Act
    AppointDictatorAction().execute(game.id, faction_0.id, {"Dictator": valerius.id}, resolver)
    AppointDictatorAction().execute(game.id, faction_1.id, {"Dictator": valerius.id}, resolver)

    # Assert
    valerius.refresh_from_db()
    assert valerius.has_title(Senator.Title.DICTATOR)


@pytest.mark.django_db
def test_consul_factions_disagree_moves_to_election(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = _setup_appointment_game(basic_game)
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.add_title(Senator.Title.FIELD_CONSUL)
    claudius.save()
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    julius = Senator.objects.get(game=game, family_name="Julius")
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    faction_0 = cornelius.faction
    faction_1 = claudius.faction
    assert faction_0 is not None
    assert faction_1 is not None

    # Act
    AppointDictatorAction().execute(game.id, faction_0.id, {"Dictator": valerius.id}, resolver)
    AppointDictatorAction().execute(game.id, faction_1.id, {"Dictator": julius.id}, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.DICTATOR_ELECTION


@pytest.mark.django_db
def test_consul_faction_skips_moves_to_election(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = _setup_appointment_game(basic_game)
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.add_title(Senator.Title.FIELD_CONSUL)
    claudius.save()
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    faction_0 = cornelius.faction
    faction_1 = claudius.faction
    assert faction_0 is not None
    assert faction_1 is not None

    # Act
    AppointDictatorAction().execute(game.id, faction_0.id, {"Dictator": valerius.id}, resolver)
    SkipAction().execute(game.id, faction_1.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.DICTATOR_ELECTION


@pytest.mark.django_db
def test_dictator_gains_7_influence(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.DICTATOR_APPOINTMENT
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    cornelius.add_title(Senator.Title.ROME_CONSUL)
    cornelius.add_title(Senator.Title.HRAO)
    cornelius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    cornelius.save()
    julius = Senator.objects.get(game=game, family_name="Julius")
    initial_influence = julius.influence

    # Act
    appoint_dictator(game.id, julius.id)

    # Assert
    julius.refresh_from_db()
    assert julius.influence == initial_influence + 7


@pytest.mark.django_db
def test_dictator_becomes_presiding_magistrate(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.DICTATOR_APPOINTMENT
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    cornelius.add_title(Senator.Title.ROME_CONSUL)
    cornelius.add_title(Senator.Title.HRAO)
    cornelius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    cornelius.save()
    julius = Senator.objects.get(game=game, family_name="Julius")

    # Act
    appoint_dictator(game.id, julius.id)

    # Assert
    julius.refresh_from_db()
    assert julius.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    cornelius.refresh_from_db()
    assert not cornelius.has_title(Senator.Title.PRESIDING_MAGISTRATE)
