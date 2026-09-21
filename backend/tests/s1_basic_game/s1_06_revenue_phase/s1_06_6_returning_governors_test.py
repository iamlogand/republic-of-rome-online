import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.effects.redistribution_done import RedistributionDoneEffect
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.elect_governor import assign_governor
from rorapp.helpers.provinces import province_static_fields
from rorapp.models import Game, Log, Province, Senator


@pytest.fixture
def governed_province(basic_game: Game) -> Province:
    game = basic_game
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.REDISTRIBUTION
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    governor = Senator.objects.filter(game=game, alive=True).order_by("id").last()
    assert governor is not None
    province = Province.objects.create(
        game=game,
        name="Sicilia",
        developed=False,
        **province_static_fields("Sicilia"),
    )
    assign_governor(province, governor)
    return province


def _end_redistribution(game: Game, resolver: FakeRandomResolver) -> None:
    RedistributionDoneEffect().execute(game.id, resolver)


@pytest.mark.django_db
def test_a_term_is_set_to_three_on_election(governed_province: Province):
    # Assert
    assert governed_province.term == 3


@pytest.mark.django_db
def test_a_term_falls_by_one_each_revenue_phase(
    governed_province: Province, resolver: FakeRandomResolver
):
    # Arrange
    game = governed_province.game

    # Act
    _end_redistribution(game, resolver)

    # Assert
    governed_province.refresh_from_db()
    assert governed_province.term == 2
    assert governed_province.governor is not None


@pytest.mark.django_db
def test_a_governor_returns_to_rome_when_his_term_runs_out(
    governed_province: Province, resolver: FakeRandomResolver
):
    # Arrange
    game = governed_province.game
    governor = governed_province.governor
    assert governor is not None
    governed_province.term = 1
    governed_province.save()

    # Act
    _end_redistribution(game, resolver)

    # Assert
    governed_province.refresh_from_db()
    governor.refresh_from_db()
    assert governed_province.governor_id is None
    assert governed_province.term is None
    assert governor.location == "Rome"
    assert Log.objects.filter(
        game=game,
        text=f"{governor.display_name} completed his term as governor of Sicilia and returned to Rome.",
    ).exists()


@pytest.mark.django_db
def test_a_returning_governor_can_retake_the_hrao(
    governed_province: Province, resolver: FakeRandomResolver
):
    # Arrange
    game = governed_province.game
    governor = governed_province.governor
    assert governor is not None
    governor.influence = 99
    governor.save()
    governed_province.term = 1
    governed_province.save()
    stand_in = Senator.objects.filter(game=game, alive=True).order_by("id").first()
    assert stand_in is not None
    stand_in.add_title(Senator.Title.HRAO)
    stand_in.save()

    # Act
    _end_redistribution(game, resolver)

    # Assert
    governor.refresh_from_db()
    assert governor.has_title(Senator.Title.HRAO)


@pytest.mark.django_db
def test_a_vacated_province_reopens_the_elections_next_senate(
    governed_province: Province, governors_enabled, resolver: FakeRandomResolver
):
    # Arrange
    game = governed_province.game
    governed_province.term = 1
    governed_province.save()
    _end_redistribution(game, resolver)

    # Act
    game.refresh_from_db()
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION


@pytest.mark.django_db
def test_the_revenue_phase_ends_normally_with_no_governors(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.REDISTRIBUTION
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    valid = RedistributionDoneEffect().validate(GameStateSnapshot(game.id))
    _end_redistribution(game, resolver)

    # Assert
    assert valid is True
    game.refresh_from_db()
    assert game.phase == Game.Phase.FORUM
