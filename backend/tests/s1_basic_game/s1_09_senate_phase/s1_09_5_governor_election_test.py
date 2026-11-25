from typing import List

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from rorapp.actions.nominate_governor import NominateGovernorAction
from rorapp.actions.vote_nay import VoteNayAction
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.auto_close_governor_elections import (
    AutoCloseGovernorElectionsEffect,
)
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.kill_senator import kill_senator
from rorapp.helpers.provinces import province_static_fields
from rorapp.models import AvailableAction, Faction, Game, Province, Senator


@pytest.fixture
def election_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    presiding = Senator.objects.filter(game=game, alive=True).order_by("id").first()
    assert presiding is not None
    presiding.add_title(Senator.Title.ROME_CONSUL)
    presiding.add_title(Senator.Title.HRAO)
    presiding.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    presiding.save()
    return game


def _add_province(game: Game, name: str) -> Province:
    return Province.objects.create(
        game=game, name=name, developed=False, **province_static_fields(name)
    )


def _presiding_faction(game: Game) -> Faction:
    senator = Senator.objects.get(
        game=game, titles__contains=Senator.Title.PRESIDING_MAGISTRATE.value
    )
    assert senator.faction is not None
    return senator.faction


def _candidates(game: Game, faction: Faction) -> List[Senator]:
    return [
        s
        for s in Senator.objects.filter(game=game, faction=faction, alive=True)
        if not s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    ]


def _option_ids(available_actions: List[AvailableAction], field_name: str) -> List[int]:
    ids: List[int] = []
    for available_action in available_actions:
        for field in available_action.field_descriptors:
            if field["name"] == field_name:
                ids.extend(option["id"] for option in field["options"])
    return ids


def _pass_the_motion(game: Game, resolver: FakeRandomResolver) -> None:
    for faction in game.factions.all():
        VoteYeaAction().execute(game.id, faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)


@pytest.mark.django_db
def test_elections_open_when_a_province_is_vacant(
    election_game: Game
):
    # Arrange
    game = election_game
    _add_province(game, "Sicilia")

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION


@pytest.mark.django_db
def test_a_won_motion_sends_the_governor_out_of_rome(
    election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = election_game
    province = _add_province(game, "Sicilia")
    execute_effects_and_manage_actions(game.id)
    faction = _presiding_faction(game)
    candidate = _candidates(game, faction)[0]

    # Act
    result = NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province.id, "Governor": candidate.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    _pass_the_motion(game, resolver)

    # Assert
    assert result.success
    province.refresh_from_db()
    candidate.refresh_from_db()
    assert province.governor_id == candidate.id
    assert candidate.location == "Sicilia"


@pytest.mark.django_db
def test_a_defeated_pairing_may_not_be_proposed_again(
    election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = election_game
    province = _add_province(game, "Sicilia")
    execute_effects_and_manage_actions(game.id)
    faction = _presiding_faction(game)
    candidate = _candidates(game, faction)[0]
    NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province.id, "Governor": candidate.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id)

    # Act
    for voting_faction in game.factions.all():
        VoteNayAction().execute(game.id, voting_faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)
    repeat = NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province.id, "Governor": candidate.id},
        resolver,
    )

    # Assert
    province.refresh_from_db()
    assert province.governor_id is None
    assert not repeat.success
    schema = NominateGovernorAction().get_schema(GameStateSnapshot(game.id), faction.id)
    assert candidate.id not in _option_ids(schema, "Governor")


@pytest.mark.django_db
def test_the_last_remaining_candidate_is_appointed_automatically(
    election_game: Game
):
    # Arrange
    game = election_game
    province = _add_province(game, "Sicilia")
    faction = _presiding_faction(game)
    sole = _candidates(game, faction)[0]
    for senator in Senator.objects.filter(game=game, alive=True).exclude(id=sole.id):
        if not senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
            senator.add_title(Senator.Title.CENSOR)
            senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    province.refresh_from_db()
    sole.refresh_from_db()
    assert province.governor_id == sole.id
    assert sole.location == "Sicilia"
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_the_sole_candidate_for_two_provinces_still_needs_a_vote(
    election_game: Game
):
    # Arrange
    game = election_game
    _add_province(game, "Sicilia")
    _add_province(game, "Macedonia")
    faction = _presiding_faction(game)
    sole = _candidates(game, faction)[0]
    for senator in Senator.objects.filter(game=game, alive=True).exclude(id=sole.id):
        if not senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
            senator.add_title(Senator.Title.CENSOR)
            senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    assert not Province.objects.filter(game=game, governor__isnull=False).exists()
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION


@pytest.mark.django_db
def test_elections_close_when_no_candidate_remains(
    election_game: Game
):
    # Arrange
    game = election_game
    _add_province(game, "Sicilia")
    game.sub_phase = Game.SubPhase.GOVERNOR_ELECTION
    game.save()
    for senator in Senator.objects.filter(game=game, alive=True):
        if not senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
            senator.add_title(Senator.Title.CENSOR)
            senator.save()

    # Act
    valid = AutoCloseGovernorElectionsEffect().validate(GameStateSnapshot(game.id))
    execute_effects_and_manage_actions(game.id)

    # Assert
    assert valid is True
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_an_elected_governor_hands_on_his_titles(
    election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = election_game
    province = _add_province(game, "Sicilia")
    execute_effects_and_manage_actions(game.id)
    faction = _presiding_faction(game)
    candidate = _candidates(game, faction)[0]
    candidate.add_title(Senator.Title.HRAO)
    presiding = Senator.objects.get(
        game=game, titles__contains=Senator.Title.PRESIDING_MAGISTRATE.value
    )
    presiding.remove_title(Senator.Title.HRAO)
    presiding.save()
    candidate.save()

    # Act
    NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province.id, "Governor": candidate.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    _pass_the_motion(game, resolver)

    # Assert
    candidate.refresh_from_db()
    assert not candidate.has_title(Senator.Title.HRAO)
    assert Senator.objects.filter(
        game=game, alive=True, titles__contains=Senator.Title.HRAO.value
    ).exists()


@pytest.mark.django_db
def test_a_governors_death_reopens_the_election(
    election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = election_game
    province = _add_province(game, "Sicilia")
    execute_effects_and_manage_actions(game.id)
    faction = _presiding_faction(game)
    candidate = _candidates(game, faction)[0]
    NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province.id, "Governor": candidate.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    _pass_the_motion(game, resolver)

    # Act
    candidate.refresh_from_db()
    kill_senator(candidate)
    execute_effects_and_manage_actions(game.id)

    # Assert
    province.refresh_from_db()
    assert province.governor_id is None
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION


@pytest.mark.django_db
def test_a_major_office_holder_is_not_a_candidate(
    election_game: Game
):
    # Arrange
    game = election_game
    _add_province(game, "Sicilia")
    execute_effects_and_manage_actions(game.id)
    faction = _presiding_faction(game)
    censor = _candidates(game, faction)[0]
    censor.add_title(Senator.Title.CENSOR)
    censor.save()

    # Act
    schema = NominateGovernorAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert censor.id not in _option_ids(schema, "Governor")


@pytest.mark.django_db
def test_an_unaligned_senator_may_be_elected(election_game: Game):
    # Arrange
    game = election_game
    _add_province(game, "Sicilia")
    execute_effects_and_manage_actions(game.id)
    unaligned = Senator.objects.create(
        family_name="Testonius",
        game=game,
        code="TST",
        military=1,
        oratory=2,
        loyalty=3,
        influence=4,
    )

    # Act
    schema = NominateGovernorAction().get_schema(
        GameStateSnapshot(game.id), _presiding_faction(game).id
    )

    # Assert
    assert unaligned.id in _option_ids(schema, "Governor")


@pytest.mark.django_db
def test_nomination_is_allowed_makes_no_database_queries(
    election_game: Game
):
    # Arrange
    game = election_game
    _add_province(game, "Sicilia")
    _add_province(game, "Macedonia")
    execute_effects_and_manage_actions(game.id)
    snapshot = GameStateSnapshot(game.id)
    action = NominateGovernorAction()

    # Act
    with CaptureQueriesContext(connection) as queries:
        for faction in snapshot.factions:
            action.is_allowed(snapshot, faction.id)

    # Assert
    assert len(queries) == 0
