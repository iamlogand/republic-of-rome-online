from typing import List

import pytest
from rorapp.actions.nominate_governor import NominateGovernorAction
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.effects.senate_phase_end import SenatePhaseEndEffect
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.elect_governor import assign_governor
from rorapp.helpers.provinces import province_static_fields
from rorapp.models import AvailableAction, Faction, Game, Log, Province, Senator


@pytest.fixture
def seated_governor(basic_game: Game) -> Province:
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
    province = Province.objects.create(
        game=game,
        name="Sicilia",
        developed=False,
        **province_static_fields("Sicilia"),
    )
    assign_governor(province, senators[-1])
    return province


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


def _end_the_senate_phase(game: Game, resolver: FakeRandomResolver) -> None:
    SenatePhaseEndEffect().execute(game.id, resolver)


@pytest.mark.django_db
def test_a_governor_may_not_be_recalled_the_turn_he_was_elected(
    seated_governor: Province
):
    # Arrange
    game = seated_governor.game
    execute_effects_and_manage_actions(game.id)

    # Act
    schema = NominateGovernorAction().get_schema(
        GameStateSnapshot(game.id), _presiding_faction(game).id
    )

    # Assert
    assert seated_governor.recently_elected is True
    assert schema == []


@pytest.mark.django_db
def test_a_recall_may_be_proposed_after_the_elections_are_over(
    seated_governor: Province, resolver: FakeRandomResolver
):
    # Arrange
    game = seated_governor.game
    _end_the_senate_phase(game, resolver)
    game.refresh_from_db()
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    execute_effects_and_manage_actions(game.id)

    # Act
    schema = NominateGovernorAction().get_schema(
        GameStateSnapshot(game.id), _presiding_faction(game).id
    )

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert seated_governor.id in _option_ids(schema, "Province")


@pytest.mark.django_db
def test_electing_a_replacement_brings_the_governor_home(
    seated_governor: Province, resolver: FakeRandomResolver
):
    # Arrange
    game = seated_governor.game
    sitting = seated_governor.governor
    assert sitting is not None
    _end_the_senate_phase(game, resolver)
    game.refresh_from_db()
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    execute_effects_and_manage_actions(game.id)
    faction = _presiding_faction(game)
    replacement = next(
        s
        for s in Senator.objects.filter(game=game, faction=faction, alive=True)
        if not s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )

    # Act
    result = NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": seated_governor.id, "Governor": replacement.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    for voting_faction in game.factions.all():
        VoteYeaAction().execute(game.id, voting_faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)

    # Assert
    assert result.success
    seated_governor.refresh_from_db()
    sitting.refresh_from_db()
    replacement.refresh_from_db()
    assert seated_governor.governor_id == replacement.id
    assert sitting.location == "Rome"
    assert replacement.location == "Sicilia"
    assert Log.objects.filter(
        game=game,
        text=f"{sitting.display_name} was recalled from Sicilia and returned to Rome.",
    ).exists()


@pytest.mark.django_db
def test_the_sitting_governor_is_not_offered_as_his_own_replacement(
    seated_governor: Province, resolver: FakeRandomResolver
):
    # Arrange
    game = seated_governor.game
    sitting = seated_governor.governor
    assert sitting is not None
    _end_the_senate_phase(game, resolver)
    game.refresh_from_db()
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    execute_effects_and_manage_actions(game.id)

    # Act
    schema = NominateGovernorAction().get_schema(
        GameStateSnapshot(game.id), _presiding_faction(game).id
    )

    # Assert
    assert sitting.id not in _option_ids(schema, "Governor")


