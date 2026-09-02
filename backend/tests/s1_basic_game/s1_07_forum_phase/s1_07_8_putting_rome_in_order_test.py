import pytest
from rorapp.classes.concession import Concession
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import EnemyLeader, Game, Log, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_major_corrupt_marker_assigned_at_senate_start(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.START
    game.save()

    senators = list(Senator.objects.filter(game=game, alive=True))
    julius = senators[0]
    julius.add_title(Senator.Title.ROME_CONSUL)
    julius.add_title(Senator.Title.HRAO)
    julius.location = "Rome"
    julius.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    julius.refresh_from_db()
    assert julius.has_status_item(Senator.StatusItem.MAJOR_CORRUPT)


def _setup_putting_rome_in_order(game: Game) -> Game:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.PUTTING_ROME_IN_ORDER
    game.save()
    return game


@pytest.mark.django_db
def test_dead_senator_revived_on_high_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    dead_senator = Senator.objects.filter(game=game, family=True).first()
    assert dead_senator is not None
    dead_senator.alive = False
    dead_senator.faction = None
    dead_senator.save()
    original_generation = dead_senator.generation
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    dead_senator.refresh_from_db()
    assert dead_senator.alive is True
    assert dead_senator.faction is None
    assert dead_senator.generation == original_generation + 1


@pytest.mark.django_db
def test_dead_senator_stays_dead_on_low_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    dead_senator = Senator.objects.filter(game=game, family=True).first()
    assert dead_senator is not None
    dead_senator.alive = False
    dead_senator.faction = None
    dead_senator.save()
    original_generation = dead_senator.generation
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [4]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    dead_senator.refresh_from_db()
    assert dead_senator.alive is False
    assert dead_senator.generation == original_generation


@pytest.mark.django_db
def test_putting_rome_in_order_advances_past_forum_phase(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    resolver = FakeRandomResolver()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert not (
        game.phase == Game.Phase.FORUM
        and game.sub_phase == Game.SubPhase.PUTTING_ROME_IN_ORDER
    )


@pytest.mark.django_db
def test_putting_rome_in_order_with_multiple_dead_senators_uses_separate_rolls(
    basic_game: Game,
):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    senators = list(Senator.objects.filter(game=game, family=True)[:2])
    assert len(senators) == 2
    for s in senators:
        s.alive = False
        s.faction = None
        s.save()
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [6, 3]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senators[0].refresh_from_db()
    senators[1].refresh_from_db()
    alive_states = sorted([senators[0].alive, senators[1].alive])
    assert alive_states == [False, True]


@pytest.mark.django_db
def test_inactive_leader_deleted_on_high_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    leader = EnemyLeader.objects.create(
        game=game,
        name="Hannibal",
        series_name="Punic",
        strength=7,
        disaster_number=9,
        standoff_number=16,
        active=False,
    )
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert not EnemyLeader.objects.filter(id=leader.id).exists()


@pytest.mark.django_db
def test_inactive_leader_survives_on_low_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    leader = EnemyLeader.objects.create(
        game=game,
        name="Hannibal",
        series_name="Punic",
        strength=7,
        disaster_number=9,
        standoff_number=16,
        active=False,
    )
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [4]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert EnemyLeader.objects.filter(id=leader.id).exists()


@pytest.mark.django_db
def test_multiple_inactive_leaders_use_separate_rolls(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    leader1 = EnemyLeader.objects.create(
        game=game,
        name="Hamilcar",
        series_name="Punic",
        strength=3,
        disaster_number=8,
        standoff_number=12,
        active=False,
    )
    leader2 = EnemyLeader.objects.create(
        game=game,
        name="Hannibal",
        series_name="Punic",
        strength=7,
        disaster_number=9,
        standoff_number=16,
        active=False,
    )
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [6, 3]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert not EnemyLeader.objects.filter(id=leader1.id).exists()
    assert EnemyLeader.objects.filter(id=leader2.id).exists()


@pytest.mark.django_db
def test_active_leader_not_rolled_for_in_putting_rome_in_order(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    leader = EnemyLeader.objects.create(
        game=game,
        name="Hannibal",
        series_name="Punic",
        strength=7,
        disaster_number=9,
        standoff_number=16,
        active=True,
    )
    resolver = FakeRandomResolver()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert EnemyLeader.objects.filter(id=leader.id).exists()


@pytest.mark.django_db
def test_destroyed_concession_rebuilt_on_high_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    game.add_destroyed_concession(Concession.MINING)
    game.save()
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert not game.has_destroyed_concession(Concession.MINING)
    assert game.has_concession(Concession.MINING)


@pytest.mark.django_db
def test_destroyed_concession_stays_destroyed_on_low_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    game.add_destroyed_concession(Concession.MINING)
    game.save()
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [4]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_destroyed_concession(Concession.MINING)
    assert not game.has_concession(Concession.MINING)


@pytest.mark.django_db
def test_multiple_destroyed_concessions_use_separate_rolls(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    game.add_destroyed_concession(Concession.MINING)
    game.add_destroyed_concession(Concession.HARBOR_FEES)
    game.save()
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [6, 3]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_concession(Concession.MINING)
    assert game.has_destroyed_concession(Concession.HARBOR_FEES)


@pytest.mark.django_db
def test_evil_omens_reduce_the_concession_revival_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    game.add_destroyed_concession(Concession.MINING)
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_destroyed_concession(Concession.MINING)


def _add_2nd_punic_war(game: Game, status: str = War.Status.ACTIVE) -> War:
    return War.objects.create(
        game=game,
        name="2nd Punic War",
        series_name="Punic",
        index=1,
        land_strength=15,
        fleet_support=5,
        naval_strength=0,
        disaster_numbers=[10],
        standoff_numbers=[11, 15],
        spoils=25,
        location="Italia",
        status=status,
    )


def _add_hannibal(game: Game, active: bool = True) -> EnemyLeader:
    return EnemyLeader.objects.create(
        game=game,
        name="Hannibal",
        series_name="Punic",
        strength=7,
        disaster_number=9,
        standoff_number=16,
        active=active,
    )


def _give_concession(game: Game, concession: Concession) -> Senator:
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_concession(concession)
    senator.save()
    return senator


@pytest.mark.django_db
def test_active_2nd_punic_war_destroys_a_tax_farmer(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    _add_2nd_punic_war(game)
    holder = _give_concession(game, Concession.LATIUM_TAX_FARMER)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [1, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    holder.refresh_from_db()
    game.refresh_from_db()
    assert not holder.has_concession(Concession.LATIUM_TAX_FARMER)
    assert game.has_destroyed_concession(Concession.LATIUM_TAX_FARMER)
    logs = Log.objects.filter(game=game)
    assert any(
        f"The 2nd Punic War destroyed the Latium tax farmer concession held by "
        f"{holder.display_name}." == log.text
        for log in logs
    )


@pytest.mark.django_db
def test_inactive_2nd_punic_war_destroys_nothing(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    _add_2nd_punic_war(game, status=War.Status.INACTIVE)
    holder = _give_concession(game, Concession.LATIUM_TAX_FARMER)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    holder.refresh_from_db()
    game.refresh_from_db()
    assert holder.has_concession(Concession.LATIUM_TAX_FARMER)
    assert not game.has_destroyed_concession(Concession.LATIUM_TAX_FARMER)


@pytest.mark.django_db
def test_active_hannibal_destroys_a_second_tax_farmer(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    _add_2nd_punic_war(game)
    _add_hannibal(game)
    holder = _give_concession(game, Concession.LATIUM_TAX_FARMER)
    _give_concession(game, Concession.ETRURIA_TAX_FARMER)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [1, 2, 1, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    holder.refresh_from_db()
    game.refresh_from_db()
    assert not holder.has_concession(Concession.LATIUM_TAX_FARMER)
    assert not holder.has_concession(Concession.ETRURIA_TAX_FARMER)
    assert game.has_destroyed_concession(Concession.LATIUM_TAX_FARMER)
    assert game.has_destroyed_concession(Concession.ETRURIA_TAX_FARMER)
    logs = Log.objects.filter(game=game)
    assert any(
        f"Hannibal destroyed the Etruria tax farmer concession held by "
        f"{holder.display_name}." == log.text
        for log in logs
    )


@pytest.mark.django_db
def test_inactive_hannibal_adds_no_tax_farmer_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    _add_2nd_punic_war(game)
    _add_hannibal(game, active=False)
    holder = _give_concession(game, Concession.LATIUM_TAX_FARMER)
    _give_concession(game, Concession.ETRURIA_TAX_FARMER)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [1, 2, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    holder.refresh_from_db()
    assert not holder.has_concession(Concession.LATIUM_TAX_FARMER)
    assert holder.has_concession(Concession.ETRURIA_TAX_FARMER)


@pytest.mark.django_db
def test_tax_farmer_not_in_play_is_left_alone(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    _add_2nd_punic_war(game)
    holder = _give_concession(game, Concession.LATIUM_TAX_FARMER)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    holder.refresh_from_db()
    game.refresh_from_db()
    assert holder.has_concession(Concession.LATIUM_TAX_FARMER)
    assert game.destroyed_concessions == []
    logs = Log.objects.filter(game=game)
    assert any(
        "The 2nd Punic War threatened the Lucania tax farmer concession, "
        "which was not in play." == log.text
        for log in logs
    )


@pytest.mark.django_db
def test_tax_farmer_destroyed_this_turn_may_be_rebuilt_the_same_turn(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    _add_2nd_punic_war(game)
    holder = _give_concession(game, Concession.LATIUM_TAX_FARMER)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [1, 5]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    holder.refresh_from_db()
    game.refresh_from_db()
    assert not holder.has_concession(Concession.LATIUM_TAX_FARMER)
    assert not game.has_destroyed_concession(Concession.LATIUM_TAX_FARMER)
    assert game.has_concession(Concession.LATIUM_TAX_FARMER)


@pytest.mark.django_db
def test_evil_omens_do_not_modify_the_tax_farmer_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    _add_2nd_punic_war(game)
    holder = _give_concession(game, Concession.LATIUM_TAX_FARMER)
    _give_concession(game, Concession.ETRURIA_TAX_FARMER)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [2, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    holder.refresh_from_db()
    assert holder.has_concession(Concession.LATIUM_TAX_FARMER)
    assert not holder.has_concession(Concession.ETRURIA_TAX_FARMER)
