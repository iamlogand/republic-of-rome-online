import pytest
from rorapp.actions.attract_knight import AttractKnightAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Faction, Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_knight_not_attracted_on_low_roll(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    assert senator is not None
    senator.talents = 10
    senator.save()

    execute_effects_and_manage_actions(game.id)

    resolver.dice_rolls = [2]

    # Act
    result = AttractKnightAction().execute(
        game.id,
        faction.id,
        {"Senator": str(senator.id), "Talents": 3},
        resolver,
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert senator.knights == 0
