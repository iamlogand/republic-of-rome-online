from typing import Sequence

import pytest
from rorapp.actions.pay_for_released_forces import PayForReleasedForcesAction
from rorapp.actions.pay_rebel_maintenance import PayRebelMaintenanceAction
from rorapp.actions.refuse_released_forces import RefuseReleasedForcesAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.hrao import set_hrao
from rorapp.models import Campaign, Game, Legion, Log, Senator, War


def _setup_rebel(
    game: Game,
    legion_numbers: Sequence[int],
    talents: int = 0,
    treasury: int = 0,
    veteran_numbers: Sequence[int] = (),
) -> Campaign:
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    rebel.rebel = True
    rebel.location = "Italia"
    rebel.talents = talents
    rebel.save()
    faction = rebel.faction
    assert faction is not None
    faction.treasury = treasury
    faction.save()

    campaign = Campaign.objects.create(game=game, war=None, commander=rebel)
    for number in legion_numbers:
        Legion.objects.create(
            game=game,
            number=number,
            campaign=campaign,
            veteran=number in veteran_numbers,
            allegiance=rebel if number in veteran_numbers else None,
        )
    War.objects.create(
        game=game,
        name="Civil War",
        index=0,
        land_strength=len(legion_numbers),
        fleet_support=0,
        naval_strength=0,
        spoils=0,
        location="Italia",
        status=War.Status.ACTIVE,
        primary_rebel=rebel,
    )
    set_hrao(game.id)
    return campaign


def _pay(game: Game, resolver: FakeRandomResolver, from_treasury: int, release=()):
    faction = Senator.objects.get(game=game, family_name="Cornelius").faction
    assert faction is not None
    selection: dict = {"Talents from the faction treasury": from_treasury}
    if release:
        selection["Legions to release"] = [str(l.id) for l in release]
    result = PayRebelMaintenanceAction().execute(
        game.id, faction.id, selection, resolver
    )
    execute_effects_and_manage_actions(game.id, resolver)
    return result


@pytest.mark.django_db
def test_rebel_pays_two_talents_per_legion(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=10)
    execute_effects_and_manage_actions(revenue_game.id, resolver)

    # Act
    result = _pay(revenue_game, resolver, from_treasury=0)

    # Assert
    assert result.success == True
    rebel = Senator.objects.get(game=revenue_game, family_name="Cornelius")
    assert rebel.talents == 4
    assert Legion.objects.filter(game=revenue_game).count() == 3


@pytest.mark.django_db
def test_maintenance_may_be_paid_from_the_faction_treasury(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2], talents=10, treasury=10)
    execute_effects_and_manage_actions(revenue_game.id, resolver)

    # Act
    _pay(revenue_game, resolver, from_treasury=4)

    # Assert
    rebel = Senator.objects.get(game=revenue_game, family_name="Cornelius")
    faction = rebel.faction
    assert faction is not None
    assert rebel.talents == 10
    assert faction.treasury == 6


@pytest.mark.django_db
def test_veterans_owing_allegiance_to_a_rebel_are_free(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=10, veteran_numbers=[1, 2])
    execute_effects_and_manage_actions(revenue_game.id, resolver)

    # Act
    _pay(revenue_game, resolver, from_treasury=0)

    # Assert
    rebel = Senator.objects.get(game=revenue_game, family_name="Cornelius")
    assert rebel.talents == 8


@pytest.mark.django_db
def test_the_state_does_not_maintain_rebel_legions(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=10)
    Legion.objects.create(game=revenue_game, number=4)

    # Act
    execute_effects_and_manage_actions(revenue_game.id, resolver)

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 200 + 100 - 20 - 2


@pytest.mark.django_db
def test_unaffordable_legions_must_be_released(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=2)
    execute_effects_and_manage_actions(revenue_game.id, resolver)
    legions = list(Legion.objects.filter(game=revenue_game).order_by("number"))

    # Act
    result = _pay(revenue_game, resolver, from_treasury=0, release=legions[1:])

    # Assert
    assert result.success == True
    legions[1].refresh_from_db()
    assert legions[1].released == True
    assert legions[1].campaign is None
    war = War.objects.get(game=revenue_game, primary_rebel__isnull=False)
    assert war.land_strength == 2


@pytest.mark.django_db
def test_releasing_affordable_legions_is_rejected(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=10)
    execute_effects_and_manage_actions(revenue_game.id, resolver)
    legions = list(Legion.objects.filter(game=revenue_game).order_by("number"))

    # Act
    result = _pay(revenue_game, resolver, from_treasury=0, release=legions[:1])

    # Assert
    assert result.success == False


@pytest.mark.django_db
def test_the_hrao_may_pay_for_released_legions(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=2)
    execute_effects_and_manage_actions(revenue_game.id, resolver)
    legions = list(Legion.objects.filter(game=revenue_game).order_by("number"))
    _pay(revenue_game, resolver, from_treasury=0, release=legions[1:])
    hrao = Senator.objects.get(game=revenue_game, titles__contains=["HRAO"])

    # Act
    assert hrao.faction_id is not None
    PayForReleasedForcesAction().execute(revenue_game.id, hrao.faction_id, {}, resolver)
    execute_effects_and_manage_actions(revenue_game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=revenue_game).count() == 3
    assert Legion.objects.filter(game=revenue_game, released=True).count() == 0
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.REDISTRIBUTION


@pytest.mark.django_db
def test_refused_legions_are_eliminated(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=2)
    execute_effects_and_manage_actions(revenue_game.id, resolver)
    legions = list(Legion.objects.filter(game=revenue_game).order_by("number"))
    _pay(revenue_game, resolver, from_treasury=0, release=legions[1:])
    hrao = Senator.objects.get(game=revenue_game, titles__contains=["HRAO"])

    # Act
    assert hrao.faction_id is not None
    RefuseReleasedForcesAction().execute(revenue_game.id, hrao.faction_id, {}, resolver)
    execute_effects_and_manage_actions(revenue_game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=revenue_game).count() == 1


@pytest.mark.django_db
def test_released_legions_are_eliminated_when_the_state_cannot_pay(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=2)
    execute_effects_and_manage_actions(revenue_game.id, resolver)
    legions = list(Legion.objects.filter(game=revenue_game).order_by("number"))
    revenue_game.refresh_from_db()
    revenue_game.state_treasury = 1
    revenue_game.save()

    # Act
    _pay(revenue_game, resolver, from_treasury=0, release=legions[1:])

    # Assert
    assert Legion.objects.filter(game=revenue_game).count() == 1
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.REDISTRIBUTION


@pytest.mark.django_db
def test_maintenance_is_only_paid_once_a_turn(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=10)
    execute_effects_and_manage_actions(revenue_game.id, resolver)
    _pay(revenue_game, resolver, from_treasury=0)

    # Act
    result = _pay(revenue_game, resolver, from_treasury=0)

    # Assert
    assert result.success == False
    rebel = Senator.objects.get(game=revenue_game, family_name="Cornelius")
    assert rebel.talents == 4


@pytest.mark.django_db
def test_a_single_released_legion_reads_as_one(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3], talents=4)
    execute_effects_and_manage_actions(revenue_game.id, resolver)
    legions = list(Legion.objects.filter(game=revenue_game).order_by("number"))

    # Act
    _pay(revenue_game, resolver, from_treasury=0, release=legions[2:])

    # Assert
    assert Log.objects.filter(
        game=revenue_game,
        text="Cornelius could not maintain 1 legion (III), which was released "
        "to the Senate.",
    ).exists()
