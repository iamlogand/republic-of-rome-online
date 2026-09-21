from typing import List

import pytest
from rorapp.actions.propose_rejecting_rhodian_alliance import (
    ProposeRejectingRhodianAllianceAction,
)
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.effects.senate_phase_end import SenatePhaseEndEffect
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.helpers.proposal_available import REJECT_RHODIAN_ALLIANCE_PROPOSAL
from rorapp.models import Campaign, Faction, Fleet, Game, Senator, War


def _setup_initiative_roll(game: Game) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
    game.deck = ["senator:18"]
    game.save()
    faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()


def _setup_senate(game: Game) -> Faction:
    game.refresh_from_db()
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None and senator.faction is not None
    senator.add_title(Senator.Title.ROME_CONSUL)
    senator.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senator.add_title(Senator.Title.HRAO)
    senator.save()
    return senator.faction


def _vote_on_rejection(game: Game, resolver: FakeRandomResolver, yea: int, nay: int) -> None:
    game.refresh_from_db()
    game.current_proposal = REJECT_RHODIAN_ALLIANCE_PROPOSAL
    game.votes_yea = yea
    game.votes_nay = nay
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    execute_effects_and_manage_actions(game.id, resolver)


def _create_war(
    game: Game,
    name: str,
    fleet_support: int,
    naval_strength: int = 0,
    status: War.Status = War.Status.ACTIVE,
    rhodian_alliance: bool = False,
) -> War:
    return War.objects.create(
        game=game,
        name=name,
        index=1,
        land_strength=10,
        fleet_support=fleet_support,
        naval_strength=naval_strength,
        spoils=10,
        location="Italy",
        status=status,
        rhodian_alliance=rhodian_alliance,
    )


def _create_fleets(game: Game, numbers: List[int], campaign: Campaign | None = None) -> None:
    for n in numbers:
        Fleet.objects.create(game=game, number=n, campaign=campaign, recently_raised=False)


def _fleet_numbers(game: Game) -> List[int]:
    return list(Fleet.objects.filter(game=game).order_by("number").values_list("number", flat=True))


def _setup_alliance(game: Game, level: int, war: War) -> None:
    for _ in range(level):
        game.add_effect(GameEffect.RHODIAN_ALLIANCE)
    game.save()
    war.rhodian_alliance = True
    war.save()


@pytest.mark.django_db
def test_rhodian_alliance_gives_the_state_8_fleets(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    _create_fleets(game, [1, 2])
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert _fleet_numbers(game) == list(range(1, 11))
    assert game.count_effect(GameEffect.RHODIAN_ALLIANCE) == 1
    assert len(game.deck) == 1


@pytest.mark.django_db
def test_rhodian_alliance_has_no_effect_when_no_war_requires_fleets(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    _create_war(game, "1st Gallic War", fleet_support=0)
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert _fleet_numbers(game) == []
    assert not game.has_effect(GameEffect.RHODIAN_ALLIANCE)
    assert len(game.deck) == 1


@pytest.mark.django_db
def test_rhodian_alliance_is_tied_to_the_war_requiring_the_most_fleets(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    punic = _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    macedonian = _create_war(game, "1st Macedonian War", fleet_support=10, status=War.Status.INACTIVE)
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    punic.refresh_from_db()
    macedonian.refresh_from_db()
    assert punic.rhodian_alliance
    assert not macedonian.rhodian_alliance


@pytest.mark.django_db
def test_an_inactive_war_can_hold_the_rhodian_alliance(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    punic = _create_war(game, "1st Punic War", fleet_support=5)
    macedonian = _create_war(game, "1st Macedonian War", fleet_support=10, status=War.Status.INACTIVE)
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    punic.refresh_from_db()
    macedonian.refresh_from_db()
    assert not punic.rhodian_alliance
    assert macedonian.rhodian_alliance


@pytest.mark.django_db
def test_rhodian_alliance_is_tied_to_every_war_sharing_the_most_fleets(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    punic = _create_war(game, "2nd Punic War", fleet_support=5)
    macedonian = _create_war(game, "2nd Macedonian War", fleet_support=5)
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    punic.refresh_from_db()
    macedonian.refresh_from_db()
    assert punic.rhodian_alliance
    assert macedonian.rhodian_alliance


@pytest.mark.django_db
def test_rhodian_fleets_count_towards_the_25_fleet_limit(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    _create_fleets(game, list(range(1, 21)))
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert _fleet_numbers(game) == list(range(1, 26))


@pytest.mark.django_db
def test_increased_rhodian_involvement_brings_the_total_to_12_fleets(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    war = _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    _setup_alliance(game, 1, war)
    _create_fleets(game, list(range(1, 9)))
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert _fleet_numbers(game) == list(range(1, 13))
    assert game.count_effect(GameEffect.RHODIAN_ALLIANCE) == 2


@pytest.mark.django_db
def test_increased_rhodian_involvement_keeps_the_original_war(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    punic = _create_war(game, "1st Punic War", fleet_support=5)
    _setup_alliance(game, 1, punic)
    macedonian = _create_war(game, "1st Macedonian War", fleet_support=10)
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    punic.refresh_from_db()
    macedonian.refresh_from_db()
    assert punic.rhodian_alliance
    assert not macedonian.rhodian_alliance


@pytest.mark.django_db
def test_rhodian_alliance_has_no_further_effect_once_increased(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    war = _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    _setup_alliance(game, 2, war)
    _create_fleets(game, list(range(1, 13)))
    resolver.dice_rolls = [7, 15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert _fleet_numbers(game) == list(range(1, 13))
    assert game.count_effect(GameEffect.RHODIAN_ALLIANCE) == 2


@pytest.mark.django_db
@pytest.mark.parametrize(
    "level, fleets_before, fleets_after",
    [
        (1, 10, 2),
        (2, 15, 3),
        (2, 5, 0),
    ],
)
def test_rhodian_fleets_are_disbanded_when_the_allied_war_is_defeated(
    basic_game: Game,
    resolver: FakeRandomResolver,
    level: int,
    fleets_before: int,
    fleets_after: int,
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    war = _create_war(game, "1st Punic War", fleet_support=5, status=War.Status.DEFEATED)
    _setup_alliance(game, level, war)
    _create_fleets(game, list(range(1, fleets_before + 1)))

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    war.refresh_from_db()
    assert len(_fleet_numbers(game)) == fleets_after
    assert not game.has_effect(GameEffect.RHODIAN_ALLIANCE)
    assert not war.rhodian_alliance


@pytest.mark.django_db
def test_reserve_fleets_are_disbanded_before_deployed_fleets(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    punic = _create_war(game, "1st Punic War", fleet_support=5, status=War.Status.DEFEATED)
    _setup_alliance(game, 1, punic)
    macedonian = _create_war(game, "1st Macedonian War", fleet_support=10)
    commander = Senator.objects.filter(game=game).first()
    assert commander is not None
    campaign = Campaign.objects.create(game=game, war=macedonian, commander=commander)
    _create_fleets(game, list(range(1, 11)), campaign)
    _create_fleets(game, list(range(11, 16)))

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert _fleet_numbers(game) == [4, 5, 6, 7, 8, 9, 10]


@pytest.mark.django_db
def test_rhodian_alliance_continues_while_its_war_is_undefeated(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    punic = _create_war(game, "1st Punic War", fleet_support=5)
    _setup_alliance(game, 1, punic)
    _create_war(game, "1st Illyrian War", fleet_support=3, status=War.Status.DEFEATED)
    _create_fleets(game, list(range(1, 11)))

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert len(_fleet_numbers(game)) == 10
    assert game.has_effect(GameEffect.RHODIAN_ALLIANCE)


@pytest.mark.django_db
def test_senate_can_reject_the_rhodian_alliance_on_the_turn_it_appears(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    _setup_initiative_roll(game)
    _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    resolver.dice_rolls = [7, 15]
    execute_effects_and_manage_actions(game.id, resolver)
    faction = _setup_senate(game)

    # Act
    allowed = ProposeRejectingRhodianAllianceAction().is_allowed(GameStateLive(game.id), faction.id)

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_senate_cannot_reject_the_rhodian_alliance_on_a_later_turn(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    war = _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    _setup_alliance(game, 1, war)
    game.rhodian_alliance_rejectable = True
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.END
    game.save()
    SenatePhaseEndEffect().execute(game.id, resolver)
    faction = _setup_senate(game)

    # Act
    allowed = ProposeRejectingRhodianAllianceAction().is_allowed(GameStateLive(game.id), faction.id)

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_rejecting_the_rhodian_alliance_disbands_its_fleets(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    war = _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    _setup_alliance(game, 1, war)
    game.rhodian_alliance_rejectable = True
    game.save()
    _setup_senate(game)
    _create_fleets(game, list(range(1, 11)))

    # Act
    _vote_on_rejection(game, resolver, yea=15, nay=0)

    # Assert
    game.refresh_from_db()
    war.refresh_from_db()
    assert len(_fleet_numbers(game)) == 2
    assert not game.has_effect(GameEffect.RHODIAN_ALLIANCE)
    assert not war.rhodian_alliance


@pytest.mark.django_db
def test_rhodian_alliance_stays_when_the_senate_does_not_reject_it(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    war = _create_war(game, "1st Punic War", fleet_support=5, naval_strength=10)
    _setup_alliance(game, 1, war)
    game.rhodian_alliance_rejectable = True
    game.save()
    faction = _setup_senate(game)
    _create_fleets(game, list(range(1, 11)))

    # Act
    _vote_on_rejection(game, resolver, yea=5, nay=10)

    # Assert
    game.refresh_from_db()
    assert len(_fleet_numbers(game)) == 10
    assert game.has_effect(GameEffect.RHODIAN_ALLIANCE)
    assert ProposeRejectingRhodianAllianceAction().is_allowed(GameStateLive(game.id), faction.id) is None
