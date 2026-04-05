import pytest
from rorapp.actions.attempt_persuasion import AttemptPersuasionAction
from rorapp.actions.counter_bribe import CounterBribeAction
from rorapp.actions.continue_persuasion import ContinuePersuasionAction
from rorapp.actions.skip import SkipAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.effects.persuasion_counter_bribe_first import (
    PersuasionCounterBribeFirstEffect,
)
from rorapp.models import Faction, Game, Senator


def _setup_persuasion_attempt(game: Game) -> tuple[Faction, Senator, Senator]:
    game.sub_phase = Game.SubPhase.PERSUASION_ATTEMPT
    game.save()

    faction1: Faction = game.factions.get(position=1)
    faction1.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction1.save()

    persuader = faction1.senators.filter(alive=True).first()
    assert persuader is not None
    persuader.oratory = 3
    persuader.influence = 2
    persuader.talents = 5
    persuader.location = "Rome"
    persuader.save()

    target = Senator.objects.create(
        game=game,
        faction=None,
        family_name="Testius",
        code="99",
        military=0,
        oratory=1,
        loyalty=4,
        influence=1,
        talents=0,
        location="Rome",
    )

    return faction1, persuader, target


def _reach_persuasion_decision(
    game: Game,
    faction1: Faction,
    persuader: Senator,
    target: Senator,
    resolver: FakeRandomResolver,
) -> None:
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
        },
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    faction2: Faction = game.factions.get(position=2)
    SkipAction().execute(game.id, faction2.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)
    faction3: Faction = game.factions.get(position=3)
    SkipAction().execute(game.id, faction3.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)


@pytest.mark.django_db
def test_attempt_persuasion_transitions_to_counter_bribe(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)

    # Act
    result = AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
        },
        resolver,
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.PERSUASION_COUNTER_BRIBE


@pytest.mark.django_db
def test_attempt_persuasion_sets_senator_status_items(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)

    # Act
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
        },
        resolver,
    )

    # Assert
    persuader.refresh_from_db()
    target.refresh_from_db()
    assert persuader.has_status_item(Senator.StatusItem.PERSUADER)
    assert target.has_status_item(Senator.StatusItem.PERSUASION_TARGET)


@pytest.mark.django_db
def test_attempt_persuasion_transfers_bribe_immediately(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)

    # Act
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "3",
        },
        resolver,
    )

    # Assert
    persuader.refresh_from_db()
    target.refresh_from_db()
    assert persuader.talents == 2
    assert target.talents == 3


@pytest.mark.django_db
def test_first_counter_briber_assigned_clockwise_from_persuader(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction2: Faction = game.factions.get(position=2)
    faction2.treasury = 5
    faction2.save()

    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
        },
        resolver,
    )

    # Act
    PersuasionCounterBribeFirstEffect().execute(game.id, resolver)

    # Assert
    faction2.refresh_from_db()
    assert faction2.has_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)


@pytest.mark.django_db
def test_counter_bribe_rotation_advances_clockwise(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
        },
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    faction2: Faction = game.factions.get(position=2)

    # Act
    SkipAction().execute(game.id, faction2.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)

    # Assert
    faction3: Faction = game.factions.get(position=3)
    faction3.refresh_from_db()
    assert faction3.has_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)


@pytest.mark.django_db
def test_counter_bribe_rotation_wraps_around_skipping_persuader(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    game.sub_phase = Game.SubPhase.PERSUASION_ATTEMPT
    game.save()
    faction2: Faction = game.factions.get(position=2)
    faction2.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction2.save()

    persuader = faction2.senators.filter(alive=True).first()
    assert persuader is not None
    persuader.oratory = 3
    persuader.influence = 2
    persuader.talents = 5
    persuader.location = "Rome"
    persuader.save()

    target = Senator.objects.create(
        game=game,
        faction=None,
        family_name="Testius",
        code="99",
        military=0,
        oratory=1,
        loyalty=4,
        influence=1,
        talents=0,
        location="Rome",
    )

    AttemptPersuasionAction().execute(
        game.id,
        faction2.id,
        {"Persuader": str(persuader.id), "Target": str(target.id), "Talents": "0"},
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    faction3: Faction = game.factions.get(position=3)

    # Act
    SkipAction().execute(game.id, faction3.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)

    # Assert
    faction1: Faction = game.factions.get(position=1)
    faction1.refresh_from_db()
    assert faction1.has_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)


@pytest.mark.django_db
def test_all_skip_counter_bribe_transitions_to_persuasion_decision(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
        },
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    faction2: Faction = game.factions.get(position=2)
    SkipAction().execute(game.id, faction2.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)

    # Act
    faction3: Faction = game.factions.get(position=3)
    SkipAction().execute(game.id, faction3.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.PERSUASION_DECISION
    assert not any(
        f.has_status_item(FactionStatusItem.COUNTER_BRIBED) for f in game.factions.all()
    )


@pytest.mark.django_db
def test_counter_bribe_transfers_money_immediately(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
        },
        resolver,
    )
    execute_effects_and_manage_actions(game.id)

    faction2: Faction = game.factions.get(position=2)
    faction2.treasury = 5
    faction2.save()

    # Act
    result = CounterBribeAction().execute(
        game.id, faction2.id, {"Talents": "3"}, resolver
    )

    # Assert
    assert result.success
    faction2.refresh_from_db()
    assert faction2.treasury == 2
    target.refresh_from_db()
    assert target.talents == 3


@pytest.mark.django_db
def test_additional_bribe_rejected_when_no_counter_bribe_made(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    _reach_persuasion_decision(game, faction1, persuader, target, resolver)

    # Act
    result = ContinuePersuasionAction().execute(
        game.id, faction1.id, {"Talents": "1"}, resolver
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_persuasion_succeeds(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    _reach_persuasion_decision(game, faction1, persuader, target, resolver)
    resolver.dice_rolls = [1, 0]

    # Act
    result = ContinuePersuasionAction().execute(
        game.id, faction1.id, {"Talents": "0"}, resolver
    )

    # Assert
    assert result.success
    target.refresh_from_db()
    assert target.faction_id == faction1.id
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT


@pytest.mark.django_db
def test_persuasion_fails(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    _reach_persuasion_decision(game, faction1, persuader, target, resolver)
    resolver.dice_rolls = [2, 3]

    # Act
    result = ContinuePersuasionAction().execute(
        game.id, faction1.id, {"Talents": "0"}, resolver
    )

    # Assert
    assert result.success
    target.refresh_from_db()
    assert target.faction_id is None
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT


@pytest.mark.django_db
def test_persuasion_clears_persuader_status_items(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    _reach_persuasion_decision(game, faction1, persuader, target, resolver)
    resolver.dice_rolls = [5, 5]

    # Act
    ContinuePersuasionAction().execute(game.id, faction1.id, {"Talents": "0"}, resolver)

    # Assert
    persuader.refresh_from_db()
    assert not persuader.has_status_item(Senator.StatusItem.PERSUADER)
    assert persuader.get_bribe_amount() is None


@pytest.mark.django_db
def test_persuasion_clears_target_status_item(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    _reach_persuasion_decision(game, faction1, persuader, target, resolver)
    resolver.dice_rolls = [5, 5]

    # Act
    ContinuePersuasionAction().execute(game.id, faction1.id, {"Talents": "0"}, resolver)

    # Assert
    target.refresh_from_db()
    assert not target.has_status_item(Senator.StatusItem.PERSUASION_TARGET)


@pytest.mark.django_db
def test_aligned_target_applies_seven_penalty_to_roll(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    game.sub_phase = Game.SubPhase.PERSUASION_ATTEMPT
    game.save()
    faction1: Faction = game.factions.get(position=1)
    faction1.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction1.save()

    persuader = faction1.senators.filter(alive=True).first()
    assert persuader is not None
    persuader.oratory = 5
    persuader.influence = 5
    persuader.talents = 0
    persuader.location = "Rome"
    persuader.save()

    faction2: Faction = game.factions.get(position=2)
    aligned_target = faction2.senators.filter(alive=True).first()
    assert aligned_target is not None
    aligned_target.loyalty = 3
    aligned_target.talents = 0
    aligned_target.location = "Rome"
    aligned_target.save()

    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(aligned_target.id),
            "Talents": "0",
        },
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    faction2_obj: Faction = game.factions.get(position=2)
    SkipAction().execute(game.id, faction2_obj.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)
    faction3: Faction = game.factions.get(position=3)
    SkipAction().execute(game.id, faction3.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)
    resolver.dice_rolls = [1, 1]

    # Act
    ContinuePersuasionAction().execute(game.id, faction1.id, {"Talents": "0"}, resolver)

    # Assert
    aligned_target.refresh_from_db()
    assert aligned_target.faction_id == faction2.id


@pytest.mark.django_db
def test_roll_equal_to_threshold_fails(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    persuader.oratory = 5
    persuader.influence = 5
    persuader.save()
    target.loyalty = 0
    target.save()
    _reach_persuasion_decision(game, faction1, persuader, target, resolver)
    resolver.dice_rolls = [5, 5]

    # Act
    ContinuePersuasionAction().execute(game.id, faction1.id, {"Talents": "0"}, resolver)

    # Assert
    target.refresh_from_db()
    assert target.faction_id is None


@pytest.mark.django_db
def test_era_ends_roll_at_threshold_fails(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    game.era_ends = True
    game.save()
    faction1, persuader, target = _setup_persuasion_attempt(game)
    persuader.oratory = 5
    persuader.influence = 5
    persuader.save()
    target.loyalty = 0
    target.save()
    _reach_persuasion_decision(game, faction1, persuader, target, resolver)
    resolver.dice_rolls = [4, 5]

    # Act
    ContinuePersuasionAction().execute(game.id, faction1.id, {"Talents": "0"}, resolver)

    # Assert
    target.refresh_from_db()
    assert target.faction_id is None


@pytest.mark.django_db
def test_era_ends_roll_below_threshold_succeeds(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    game.era_ends = True
    game.save()
    faction1, persuader, target = _setup_persuasion_attempt(game)
    persuader.oratory = 5
    persuader.influence = 5
    persuader.save()
    target.loyalty = 0
    target.save()
    _reach_persuasion_decision(game, faction1, persuader, target, resolver)
    resolver.dice_rolls = [3, 5]

    # Act
    ContinuePersuasionAction().execute(game.id, faction1.id, {"Talents": "0"}, resolver)

    # Assert
    target.refresh_from_db()
    assert target.faction_id == faction1.id


@pytest.mark.django_db
def test_seduction_resolves_immediately(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction1.add_card("seduction")
    faction1.save()
    resolver.dice_rolls = [1, 0]

    # Act
    result = AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
            "Seduction": True,
        },
        resolver,
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT


@pytest.mark.django_db
def test_seduction_consumes_card(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction1.add_card("seduction")
    faction1.save()
    resolver.dice_rolls = [1, 0]

    # Act
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
            "Seduction": True,
        },
        resolver,
    )

    # Assert
    faction1.refresh_from_db()
    assert not faction1.has_card("seduction")


@pytest.mark.django_db
def test_blackmail_resolves_immediately(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction1.add_card("blackmail")
    faction1.save()
    resolver.dice_rolls = [1, 0]

    # Act
    result = AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
            "Blackmail": True,
        },
        resolver,
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT


@pytest.mark.django_db
def test_blackmail_consumes_card(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction1.add_card("blackmail")
    faction1.save()
    resolver.dice_rolls = [1, 0]

    # Act
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
            "Blackmail": True,
        },
        resolver,
    )

    # Assert
    faction1.refresh_from_db()
    assert not faction1.has_card("blackmail")


@pytest.mark.django_db
def test_blackmail_applies_penalty_on_failure(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction1.add_card("blackmail")
    faction1.save()
    target.influence = 5
    target.popularity = 4
    target.save()
    resolver.dice_rolls = [5, 5, 3, 2, 2, 1]

    # Act
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
            "Blackmail": True,
        },
        resolver,
    )

    # Assert
    target.refresh_from_db()
    assert target.faction_id is None
    assert target.influence == 0
    assert target.popularity == 1


@pytest.mark.django_db
def test_blackmail_no_penalty_on_success(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction1.add_card("blackmail")
    faction1.save()
    target.influence = 5
    target.popularity = 4
    target.save()
    resolver.dice_rolls = [1, 0]

    # Act
    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
            "Blackmail": True,
        },
        resolver,
    )

    # Assert
    target.refresh_from_db()
    assert target.faction_id == faction1.id
    assert target.influence == 5
    assert target.popularity == 4


@pytest.mark.django_db
def test_seduction_rejected_without_card(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)

    # Act
    result = AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
            "Seduction": True,
        },
        resolver,
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_both_cards_rejected(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction1.add_card("seduction")
    faction1.add_card("blackmail")
    faction1.save()

    # Act
    result = AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
            "Seduction": True,
            "Blackmail": True,
        },
        resolver,
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_additional_bribe_triggers_new_counter_bribe_round(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction1, persuader, target = _setup_persuasion_attempt(game)
    faction2: Faction = game.factions.get(position=2)
    faction2.treasury = 10
    faction2.save()

    AttemptPersuasionAction().execute(
        game.id,
        faction1.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(target.id),
            "Talents": "0",
        },
        resolver,
    )
    execute_effects_and_manage_actions(game.id)
    CounterBribeAction().execute(game.id, faction2.id, {"Talents": "2"}, resolver)
    execute_effects_and_manage_actions(game.id)
    faction3: Faction = game.factions.get(position=3)
    SkipAction().execute(game.id, faction3.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)

    result = ContinuePersuasionAction().execute(
        game.id, faction1.id, {"Talents": "3"}, resolver
    )
    assert result.success
    execute_effects_and_manage_actions(game.id)
    faction2.refresh_from_db()
    SkipAction().execute(game.id, faction2.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)
    faction3.refresh_from_db()
    SkipAction().execute(game.id, faction3.id, {}, resolver)
    execute_effects_and_manage_actions(game.id)
    resolver.dice_rolls = [1, 1]

    # Act
    result = ContinuePersuasionAction().execute(
        game.id, faction1.id, {"Talents": "0"}, resolver
    )

    # Assert
    assert result.success
    target.refresh_from_db()
    assert target.faction_id == faction1.id
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT
