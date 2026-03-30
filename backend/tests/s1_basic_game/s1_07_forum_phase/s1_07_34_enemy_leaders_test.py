import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import EnemyLeader, Faction, Game, War


def _setup_initiative_roll(game: Game, faction: Faction, deck: list) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
    game.deck = deck
    game.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()


@pytest.mark.django_db
def test_drawing_leader_with_no_matching_wars_creates_inactive_leader(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction, ["leader:Hannibal"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader = EnemyLeader.objects.get(game=game, name="Hannibal")
    assert leader.active is False


@pytest.mark.django_db
def test_drawing_leader_with_matching_active_war_creates_active_leader(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=10,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )
    _setup_initiative_roll(game, faction, ["leader:Hannibal"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader = EnemyLeader.objects.get(game=game, name="Hannibal")
    assert leader.active is True


@pytest.mark.django_db
def test_drawing_leader_with_matching_inactive_war_activates_war_and_leader(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=10,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.INACTIVE,
    )
    _setup_initiative_roll(game, faction, ["leader:Hannibal"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader = EnemyLeader.objects.get(game=game, name="Hannibal")
    assert leader.active is True
    war.refresh_from_db()
    assert war.status == War.Status.ACTIVE


@pytest.mark.django_db
def test_drawing_leader_with_only_imminent_matching_war_creates_inactive_leader(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=10,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.IMMINENT,
    )
    _setup_initiative_roll(game, faction, ["leader:Hannibal"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader = EnemyLeader.objects.get(game=game, name="Hannibal")
    assert leader.active is False
    war.refresh_from_db()
    assert war.status == War.Status.IMMINENT


@pytest.mark.django_db
def test_drawing_leader_with_multiple_inactive_matching_wars_activates_all(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    war1 = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=10,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.INACTIVE,
    )
    war2 = War.objects.create(
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
        status=War.Status.INACTIVE,
    )
    _setup_initiative_roll(game, faction, ["leader:Hannibal"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader = EnemyLeader.objects.get(game=game, name="Hannibal")
    assert leader.active is True
    war1.refresh_from_db()
    assert war1.status == War.Status.ACTIVE
    war2.refresh_from_db()
    assert war2.status == War.Status.ACTIVE


@pytest.mark.django_db
def test_drawing_leader_uses_correct_stats_from_game_data(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction, ["leader:Hamilcar"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader = EnemyLeader.objects.get(game=game, name="Hamilcar")
    assert leader.strength == 3
    assert leader.disaster_number == 8
    assert leader.standoff_number == 12
