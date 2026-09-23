import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import AvailableAction, Faction, Game, Senator


def _setup_faction_leader_step(game: Game, faction: Faction) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.FACTION_LEADER
    game.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.add_initiative(6)
    faction.save()


@pytest.mark.django_db
def test_faction_without_senators_does_not_stall_the_faction_leader_step(
    basic_game: Game,
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    Senator.objects.filter(game=game, faction=faction).delete()
    _setup_faction_leader_step(game, faction)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    faction.refresh_from_db()
    assert game.sub_phase != Game.SubPhase.FACTION_LEADER
    assert not faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)


@pytest.mark.django_db
def test_faction_with_senators_still_selects_a_faction_leader(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_faction_leader_step(game, faction)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.FACTION_LEADER
    assert AvailableAction.objects.filter(
        game=game, faction=faction, base_name="Select faction leader"
    ).exists()
