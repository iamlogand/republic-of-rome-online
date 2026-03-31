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
def test_drawing_war_with_no_matching_war_creates_inactive_war(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction, ["war:1st Punic War"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war = War.objects.get(game=game, name="1st Punic War")
    assert war.status == War.Status.INACTIVE


@pytest.mark.django_db
def test_drawing_immediately_active_war_creates_active_war(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction, ["war:2nd Punic War"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war = War.objects.get(game=game, name="2nd Punic War")
    assert war.status == War.Status.ACTIVE


@pytest.mark.django_db
def test_drawing_war_matching_existing_inactive_war_becomes_imminent(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    existing_war = War.objects.create(
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
    _setup_initiative_roll(game, faction, ["war:1st Punic War"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    drawn_war = War.objects.get(game=game, name="1st Punic War")
    assert drawn_war.status == War.Status.IMMINENT
    existing_war.refresh_from_db()
    assert existing_war.status == War.Status.ACTIVE


@pytest.mark.django_db
def test_drawing_war_matching_existing_active_war_becomes_imminent(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    existing_war = War.objects.create(
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
        status=War.Status.ACTIVE,
    )
    _setup_initiative_roll(game, faction, ["war:1st Punic War"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    drawn_war = War.objects.get(game=game, name="1st Punic War")
    assert drawn_war.status == War.Status.IMMINENT
    existing_war.refresh_from_db()
    assert existing_war.status == War.Status.ACTIVE


@pytest.mark.django_db
def test_drawing_war_with_inactive_leader_activates_leader(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    leader = EnemyLeader.objects.create(
        game=game,
        name="Hamilcar",
        series_name="Punic",
        strength=3,
        disaster_number=8,
        standoff_number=12,
        active=False,
    )
    _setup_initiative_roll(game, faction, ["war:1st Punic War"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader.refresh_from_db()
    assert leader.active is True



@pytest.mark.django_db
def test_drawing_immediately_active_war_with_inactive_leader_creates_active_war(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    leader = EnemyLeader.objects.create(
        game=game,
        name="Hamilcar",
        series_name="Punic",
        strength=3,
        disaster_number=8,
        standoff_number=12,
        active=False,
    )
    _setup_initiative_roll(game, faction, ["war:2nd Punic War"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war = War.objects.get(game=game, name="2nd Punic War")
    assert war.status == War.Status.ACTIVE
    leader.refresh_from_db()
    assert leader.active is True
