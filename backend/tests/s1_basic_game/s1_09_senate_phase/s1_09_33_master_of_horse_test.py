import pytest
from rorapp.actions.select_master_of_horse import SelectMasterOfHorseAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.transfer_power_consuls import transfer_power_consuls
from rorapp.models import Game, Senator


def _setup_moh_appointment(game: Game) -> tuple:
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.MASTER_OF_HORSE_APPOINTMENT
    game.save()
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.DICTATOR)
    julius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.add_title(Senator.Title.HRAO)
    julius.save()
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    faction_0 = julius.faction
    return game, julius, valerius, faction_0


@pytest.mark.django_db
def test_dictator_faction_selects_master_of_horse(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, julius, valerius, faction_0 = _setup_moh_appointment(basic_game)
    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = SelectMasterOfHorseAction().is_allowed(snapshot, faction_0.id)

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_master_of_horse_gains_3_influence(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, julius, valerius, faction_0 = _setup_moh_appointment(basic_game)
    initial_influence = valerius.influence

    # Act
    SelectMasterOfHorseAction().execute(game.id, faction_0.id, {"Master of Horse": valerius.id}, resolver)

    # Assert
    valerius.refresh_from_db()
    assert valerius.influence == initial_influence + 3


@pytest.mark.django_db
def test_master_of_horse_gets_title(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, julius, valerius, faction_0 = _setup_moh_appointment(basic_game)

    # Act
    SelectMasterOfHorseAction().execute(game.id, faction_0.id, {"Master of Horse": valerius.id}, resolver)

    # Assert
    valerius.refresh_from_db()
    assert valerius.has_title(Senator.Title.MASTER_OF_HORSE)


@pytest.mark.django_db
def test_moh_appointment_advances_to_censor_election(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, julius, valerius, faction_0 = _setup_moh_appointment(basic_game)

    # Act
    SelectMasterOfHorseAction().execute(game.id, faction_0.id, {"Master of Horse": valerius.id}, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.CENSOR_ELECTION


@pytest.mark.django_db
def test_dictator_and_moh_titles_cleared_at_next_consular_elections(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.DICTATOR)
    julius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.add_title(Senator.Title.HRAO)
    julius.save()
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    valerius.add_title(Senator.Title.MASTER_OF_HORSE)
    valerius.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")

    # Act
    transfer_power_consuls(game.id, cornelius.id, fabius.id)

    # Assert
    julius.refresh_from_db()
    assert not julius.has_title(Senator.Title.DICTATOR)
    valerius.refresh_from_db()
    assert not valerius.has_title(Senator.Title.MASTER_OF_HORSE)


@pytest.mark.django_db
def test_dictator_gets_prior_consul_at_term_end(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.DICTATOR)
    julius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.add_title(Senator.Title.HRAO)
    julius.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")

    # Act
    transfer_power_consuls(game.id, cornelius.id, fabius.id)

    # Assert
    julius.refresh_from_db()
    assert julius.has_title(Senator.Title.PRIOR_CONSUL)


@pytest.mark.django_db
def test_moh_does_not_get_prior_consul_at_term_end(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.DICTATOR)
    julius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.add_title(Senator.Title.HRAO)
    julius.save()
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    valerius.add_title(Senator.Title.MASTER_OF_HORSE)
    valerius.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")

    # Act
    transfer_power_consuls(game.id, cornelius.id, fabius.id)

    # Assert
    valerius.refresh_from_db()
    assert not valerius.has_title(Senator.Title.PRIOR_CONSUL)
