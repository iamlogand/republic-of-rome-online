from typing import List

import pytest
from rorapp.actions.accept_governorship import AcceptGovernorshipAction
from rorapp.actions.accept_risky_command import AcceptRiskyCommandAction
from rorapp.actions.nominate_governor import NominateGovernorAction
from rorapp.actions.refuse_governorship import RefuseGovernorshipAction
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.provinces import province_static_fields
from rorapp.models import AvailableAction, Faction, Game, Log, Province, Senator


@pytest.fixture
def returned_governor(basic_game: Game) -> Senator:
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True).order_by("id"))
    presiding = senators[0]
    presiding.add_title(Senator.Title.ROME_CONSUL)
    presiding.add_title(Senator.Title.HRAO)
    presiding.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    presiding.save()
    Province.objects.create(
        game=game,
        name="Sicilia",
        developed=False,
        **province_static_fields("Sicilia"),
    )
    returned = senators[-1]
    returned.add_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
    returned.save()
    return returned


def _province(game: Game) -> Province:
    return Province.objects.get(game=game, name="Sicilia")


def _presiding_faction(game: Game) -> Faction:
    senator = Senator.objects.get(
        game=game, titles__contains=Senator.Title.PRESIDING_MAGISTRATE.value
    )
    assert senator.faction is not None
    return senator.faction


def _option_ids(available_actions: List[AvailableAction], field_name: str) -> List[int]:
    ids: List[int] = []
    for available_action in available_actions:
        for field in available_action.field_descriptors:
            if field["name"] == field_name:
                ids.extend(option["id"] for option in field["options"])
    return ids


def _nominate(game: Game, senator: Senator, resolver: FakeRandomResolver):
    faction = _presiding_faction(game)
    result = NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": _province(game).id, "Governor": senator.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    return result


@pytest.mark.django_db
def test_nominating_a_returned_governor_asks_his_faction_to_consent(
    returned_governor: Senator, governors_enabled, resolver: FakeRandomResolver
):
    # Arrange
    game = returned_governor.game
    execute_effects_and_manage_actions(game.id)

    # Act
    result = _nominate(game, returned_governor, resolver)

    # Assert
    assert result.success
    returned_governor.refresh_from_db()
    assert returned_governor.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
    assert Log.objects.filter(
        game=game,
        text__endswith=f"{returned_governor.display_name} must consent to govern again this turn.",
    ).exists()


@pytest.mark.django_db
def test_accepting_lets_the_vote_go_ahead(
    returned_governor: Senator, governors_enabled, resolver: FakeRandomResolver
):
    # Arrange
    game = returned_governor.game
    execute_effects_and_manage_actions(game.id)
    _nominate(game, returned_governor, resolver)
    assert returned_governor.faction is not None

    # Act
    result = AcceptGovernorshipAction().execute(
        game.id, returned_governor.faction.id, {}, resolver
    )
    execute_effects_and_manage_actions(game.id)
    for faction in game.factions.all():
        VoteYeaAction().execute(game.id, faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)

    # Assert
    assert result.success
    returned_governor.refresh_from_db()
    assert _province(game).governor_id == returned_governor.id
    assert returned_governor.location == "Sicilia"
    assert not returned_governor.has_status_item(Senator.StatusItem.RETURNED_GOVERNOR)


@pytest.mark.django_db
def test_refusing_withdraws_the_motion(
    returned_governor: Senator, governors_enabled, resolver: FakeRandomResolver
):
    # Arrange
    game = returned_governor.game
    execute_effects_and_manage_actions(game.id)
    _nominate(game, returned_governor, resolver)
    assert returned_governor.faction is not None

    # Act
    result = RefuseGovernorshipAction().execute(
        game.id, returned_governor.faction.id, {}, resolver
    )
    execute_effects_and_manage_actions(game.id)

    # Assert
    assert result.success
    game.refresh_from_db()
    assert not game.current_proposal
    assert game.defeated_proposals == []
    assert _province(game).governor_id is None
    assert Log.objects.filter(
        game=game,
        text=f"{returned_governor.display_name} refused to govern again.",
    ).exists()


@pytest.mark.django_db
def test_no_consent_is_needed_when_every_candidate_has_returned(
    returned_governor: Senator, governors_enabled, resolver: FakeRandomResolver
):
    # Arrange
    game = returned_governor.game
    for senator in Senator.objects.filter(game=game, alive=True):
        if not senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
            senator.add_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
            senator.save()
    execute_effects_and_manage_actions(game.id)

    # Act
    result = _nominate(game, returned_governor, resolver)

    # Assert
    assert result.success
    returned_governor.refresh_from_db()
    assert not returned_governor.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)


@pytest.mark.django_db
def test_an_unaligned_returned_governor_is_not_offered(
    returned_governor: Senator, governors_enabled
):
    # Arrange
    game = returned_governor.game
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
    unaligned.add_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
    unaligned.save()

    # Act
    schema = NominateGovernorAction().get_schema(
        GameStateSnapshot(game.id), _presiding_faction(game).id
    )

    # Assert
    assert unaligned.id not in _option_ids(schema, "Governor")
    assert returned_governor.id in _option_ids(schema, "Governor")


@pytest.mark.django_db
def test_a_governorship_is_not_offered_as_a_risky_command(
    returned_governor: Senator, governors_enabled, resolver: FakeRandomResolver
):
    # Arrange
    game = returned_governor.game
    execute_effects_and_manage_actions(game.id)
    _nominate(game, returned_governor, resolver)
    assert returned_governor.faction is not None

    # Act
    faction = AcceptRiskyCommandAction().is_allowed(
        GameStateSnapshot(game.id), returned_governor.faction.id
    )

    # Assert
    assert faction is None
