import pytest
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game


def _setup_initiative_roll(game: Game, faction: Faction) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
    game.deck = ["senator:18"]
    game.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_allied_enthusiasm(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_effect(GameEffect.ALLIED_ENTHUSIASM)
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 1


@pytest.mark.django_db
def test_rolling_7_does_not_draw_a_card(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert len(game.deck) == 1


@pytest.mark.django_db
def test_drawing_allied_enthusiasm_twice_escalates_to_extreme(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 2


@pytest.mark.django_db
def test_rolling_unimplemented_event_draws_a_card_instead(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [
        7,
        11,
    ]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert len(game.deck) == 0


@pytest.mark.django_db
def test_rolling_7_with_evil_omens_event_roll_adds_effect(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_effect(GameEffect.EVIL_OMENS)
    assert game.count_effect(GameEffect.EVIL_OMENS) == 1


@pytest.mark.django_db
def test_evil_omens_costs_20T_on_first_draw(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 80


@pytest.mark.django_db
def test_evil_omens_second_draw_does_not_cost_additional_20T(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 100



@pytest.mark.django_db
def test_evil_omens_does_not_affect_initiative_roll(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_effect(GameEffect.ALLIED_ENTHUSIASM)


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_drought(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 9]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.DROUGHT) == 1


@pytest.mark.django_db
def test_drawing_drought_beyond_severe_still_increases_famine(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.DROUGHT)
    game.add_effect(GameEffect.DROUGHT)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 9]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.DROUGHT) == 3


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_manpower_shortage(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 12]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.MANPOWER_SHORTAGE) == 1


@pytest.mark.django_db
def test_drawing_manpower_shortage_twice_stacks(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.MANPOWER_SHORTAGE)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 12]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.MANPOWER_SHORTAGE) == 2


@pytest.mark.django_db
def test_drawing_allied_enthusiasm_at_max_has_no_effect(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 2


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_epidemic(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["1"]]
    victim = game.senators.get(code="1")

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    victim.refresh_from_db()
    assert victim.alive == False


@pytest.mark.django_db
def test_epidemic_kills_every_senator_in_rome_that_is_drawn(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["1", "5"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert game.senators.filter(code="1", alive=True).count() == 0
    assert game.senators.filter(code="5", alive=True).count() == 0


@pytest.mark.django_db
def test_epidemic_does_not_kill_senators_away_from_rome(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    commander = game.senators.get(code="1")
    commander.location = "Sicilia"
    commander.save()
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["1"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.alive == True




@pytest.mark.django_db
def test_epidemic_without_matching_chits_kills_nobody(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["21", "22", "23", "24", "25", "26"]]
    senator_count = game.senators.filter(alive=True).count()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert game.senators.filter(alive=True).count() == senator_count


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_natural_disaster(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.NATURAL_DISASTER) == 1


@pytest.mark.django_db
def test_natural_disaster_costs_50T_on_first_draw(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 50


@pytest.mark.django_db
def test_natural_disaster_second_draw_does_not_cost_additional_50T(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.add_effect(GameEffect.NATURAL_DISASTER)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 100


@pytest.mark.django_db
def test_natural_disaster_second_draw_still_destroys_a_concession(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.NATURAL_DISASTER)
    game.add_concession(Concession.MINING)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.NATURAL_DISASTER) == 2
    assert game.has_destroyed_concession(Concession.MINING)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "concession_roll, concession",
    [
        (1, Concession.MINING),
        (2, Concession.MINING),
        (3, Concession.HARBOR_FEES),
        (4, Concession.HARBOR_FEES),
        (5, Concession.ARMAMENTS),
        (6, Concession.SHIP_BUILDING),
    ],
)
def test_natural_disaster_destroys_the_rolled_concession(
    basic_game: Game,
    resolver: FakeRandomResolver,
    concession_roll: int,
    concession: Concession,
):
    # Arrange
    game = basic_game
    for value in Concession:
        game.add_concession(value)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, concession_roll]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.destroyed_concessions == [concession.value]
    assert not game.has_concession(concession)


@pytest.mark.django_db
def test_natural_disaster_takes_the_concession_from_its_holder(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    holder = game.senators.get(code="1")
    holder.add_concession(Concession.MINING)
    holder.add_corrupt_concession(Concession.MINING)
    holder.save()
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    holder.refresh_from_db()
    assert not holder.has_concession(Concession.MINING)
    assert not holder.has_corrupt_concession(Concession.MINING)
    assert game.has_destroyed_concession(Concession.MINING)
    assert not game.has_concession(Concession.MINING)


@pytest.mark.django_db
def test_natural_disaster_has_no_effect_on_a_concession_out_of_play(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    faction.add_card(f"concession:{Concession.MINING.value}")
    faction.save()
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    faction.refresh_from_db()
    assert game.destroyed_concessions == []
    assert faction.has_card(f"concession:{Concession.MINING.value}")


@pytest.mark.django_db
def test_natural_disaster_does_not_destroy_an_already_destroyed_concession(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_destroyed_concession(Concession.MINING)
    game.add_concession(Concession.MINING)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_concession(Concession.MINING)


@pytest.mark.django_db
def test_evil_omens_do_not_modify_the_natural_disaster_roll(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.add_concession(Concession.MINING)
    game.add_concession(Concession.HARBOR_FEES)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 3]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_destroyed_concession(Concession.HARBOR_FEES)
    assert not game.has_destroyed_concession(Concession.MINING)


@pytest.mark.django_db
def test_widespread_natural_disaster_destroys_more_without_further_payment(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.add_concession(Concession.MINING)
    game.add_concession(Concession.ARMAMENTS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)
    game.refresh_from_db()
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 5]
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.NATURAL_DISASTER) == 2
    assert game.state_treasury == 50
    assert game.has_destroyed_concession(Concession.MINING)
    assert game.has_destroyed_concession(Concession.ARMAMENTS)
