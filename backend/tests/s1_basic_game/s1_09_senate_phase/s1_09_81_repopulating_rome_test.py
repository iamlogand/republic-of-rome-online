import pytest

from rorapp.actions.select_senator import SelectSenatorAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.effects.repopulate_rome import RepopulateRomeEffect
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.kill_senator import kill_senator
from rorapp.models import AvailableAction, Faction, Game, Senator


def _senator(game: Game, family_name: str) -> Senator:
    return Senator.objects.get(game=game, family_name=family_name, family=True)


def _faction(game: Game, position: int) -> Faction:
    return Faction.objects.get(game=game, position=position)


def _send_to_curia(game: Game, *family_names: str) -> None:
    for position, family_name in enumerate(family_names, start=1):
        senator = _senator(game, family_name)
        senator.alive = False
        senator.faction = None
        senator.curia_position = position
        senator.save()


def _unalign(game: Game, *family_names: str) -> None:
    for family_name in family_names:
        senator = _senator(game, family_name)
        senator.faction = None
        senator.save()


def _send_abroad(game: Game, *family_names: str) -> None:
    for family_name in family_names:
        senator = _senator(game, family_name)
        senator.location = "Sicilia"
        senator.save()


def _play_fabius_statesman(game: Game, faction: Faction) -> Senator:
    return Senator.objects.create(
        game=game,
        faction=faction,
        family_name="Fabius",
        family=False,
        code="2a",
        statesman_name="Q. Fabius Maximus Verrucosus Cunctator",
        military=5,
        oratory=2,
        loyalty=7,
        influence=3,
    )


@pytest.mark.django_db
def test_senator_who_died_first_is_promoted_first(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    for family_name in ("Furius", "Aurelius", "Junius"):
        kill_senator(_senator(senate_game, family_name))

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    furius = _senator(senate_game, "Furius")
    assert furius.alive
    assert furius.generation == 2
    assert furius.faction == _faction(senate_game, 3)
    assert furius.curia_position is None
    assert not _senator(senate_game, "Aurelius").alive
    assert not _senator(senate_game, "Junius").alive


@pytest.mark.django_db
def test_promotions_continue_until_8_aligned_senators_are_in_rome(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_to_curia(senate_game, "Furius", "Aurelius", "Junius", "Julius")

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    assert _senator(senate_game, "Furius").alive
    assert _senator(senate_game, "Aurelius").alive
    assert not _senator(senate_game, "Junius").alive
    assert not _senator(senate_game, "Julius").alive


@pytest.mark.django_db
def test_no_promotion_while_8_aligned_senators_are_in_rome(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_to_curia(senate_game, "Furius", "Aurelius")

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    assert not _senator(senate_game, "Furius").alive
    assert not _senator(senate_game, "Aurelius").alive


@pytest.mark.django_db
def test_promoted_senator_joins_the_faction_with_the_fewest_senators(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_to_curia(senate_game, "Furius", "Aurelius", "Junius")

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    assert _senator(senate_game, "Furius").faction == _faction(senate_game, 3)


@pytest.mark.django_db
def test_factions_tied_on_senators_are_separated_by_least_influence_in_rome(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_to_curia(senate_game, "Fabius", "Valerius", "Claudius")

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    assert _senator(senate_game, "Fabius").faction == _faction(senate_game, 2)


@pytest.mark.django_db
def test_factions_tied_on_influence_are_separated_by_a_dice_roll(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_to_curia(senate_game, "Fabius", "Valerius", "Claudius")
    julius = _senator(senate_game, "Julius")
    julius.influence = 3
    julius.save()
    resolver.dice_rolls = [6, 1]

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    assert _senator(senate_game, "Fabius").faction == _faction(senate_game, 1)


@pytest.mark.django_db
def test_senators_outside_rome_do_not_count_towards_the_8(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_to_curia(senate_game, "Junius")
    _send_abroad(senate_game, "Fabius", "Valerius")

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    junius = _senator(senate_game, "Junius")
    assert junius.alive
    assert junius.faction == _faction(senate_game, 3)


@pytest.mark.django_db
def test_faction_is_asked_to_choose_when_no_dead_senators_remain(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _unalign(senate_game, "Fabius", "Valerius", "Claudius")

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    senate_game.refresh_from_db()
    assert senate_game.sub_phase == Game.SubPhase.REPOPULATION
    assert senate_game.interrupted_sub_phase == Game.SubPhase.OTHER_BUSINESS
    faction = _faction(senate_game, 2)
    assert faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert AvailableAction.objects.filter(
        game=senate_game, faction=faction, base_name=SelectSenatorAction.NAME
    ).exists()


@pytest.mark.django_db
def test_chosen_senator_joins_the_faction_and_the_senate_resumes(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _unalign(senate_game, "Fabius", "Valerius", "Claudius")
    execute_effects_and_manage_actions(senate_game.id, resolver)
    faction = _faction(senate_game, 2)
    fabius = _senator(senate_game, "Fabius")

    # Act
    SelectSenatorAction().execute(
        senate_game.id, faction.id, {"Senator": fabius.id}, resolver
    )
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    assert _senator(senate_game, "Fabius").faction == faction
    senate_game.refresh_from_db()
    assert senate_game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert senate_game.interrupted_sub_phase == ""
    assert not _faction(senate_game, 2).has_status_item(
        FactionStatusItem.AWAITING_DECISION
    )


@pytest.mark.django_db
def test_senator_matching_a_played_statesman_is_passed_over(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_to_curia(senate_game, "Fabius", "Furius", "Aurelius", "Junius")
    _play_fabius_statesman(senate_game, _faction(senate_game, 1))

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    assert _senator(senate_game, "Furius").alive
    assert _senator(senate_game, "Furius").faction == _faction(senate_game, 3)
    assert not _senator(senate_game, "Fabius").alive


@pytest.mark.django_db
def test_faction_chooses_when_every_dead_senator_matches_a_played_statesman(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_to_curia(senate_game, "Fabius")
    _play_fabius_statesman(senate_game, _faction(senate_game, 1))
    _unalign(senate_game, "Claudius", "Manlius", "Fulvius")

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    senate_game.refresh_from_db()
    assert senate_game.sub_phase == Game.SubPhase.REPOPULATION
    assert _faction(senate_game, 2).has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert not _senator(senate_game, "Fabius").alive


@pytest.mark.django_db
def test_no_promotion_when_no_senators_are_available(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _send_abroad(senate_game, "Fabius", "Valerius", "Claudius")

    # Act
    execute_effects_and_manage_actions(senate_game.id, resolver)

    # Assert
    senate_game.refresh_from_db()
    assert senate_game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert Senator.objects.filter(game=senate_game, alive=True).count() == 10


@pytest.mark.django_db
def test_no_promotion_outside_the_senate_phase(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    basic_game.phase = Game.Phase.FORUM
    basic_game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
    basic_game.save()
    _send_to_curia(basic_game, "Furius", "Aurelius", "Junius")

    # Act
    valid = RepopulateRomeEffect().validate(GameStateSnapshot(basic_game.id))

    # Assert
    assert valid is False
