import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.initiative_next import InitiativeNextEffect
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game


@pytest.mark.django_db
def test_last_initiative_transitions_to_putting_rome_in_order(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.END
    game.save()

    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.initiative(6))
    faction.save()

    # Act
    InitiativeNextEffect().execute(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    assert game.phase == Game.Phase.FORUM
    assert game.sub_phase == Game.SubPhase.PUTTING_ROME_IN_ORDER


@pytest.mark.django_db
def test_last_initiative_clears_all_initiative_status_items(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.END
    game.save()

    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    faction1.add_status_item(FactionStatusItem.initiative(6))
    faction1.add_status_item(FactionStatusItem.initiative(3))
    faction2.add_status_item(FactionStatusItem.initiative(1))
    faction1.save()
    faction2.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    for faction in Faction.objects.filter(game=game):
        for i in Faction.INITIATIVE_INDICES:
            assert not faction.has_status_item(FactionStatusItem.initiative(i))
