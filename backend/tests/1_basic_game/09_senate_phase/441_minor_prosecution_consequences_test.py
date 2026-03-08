import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game, Senator


def _setup_all_factions_done(game: Game):
    for f in Faction.objects.filter(game=game):
        f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
        f.add_status_item(FactionStatusItem.DONE)
        f.save()


@pytest.mark.django_db
def test_minor_prosecution_guilty(prosecution_setup, resolver: FakeRandomResolver):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup
    prosecutor_influence_before = scipio.influence

    game.current_proposal = f"Prosecute {cornelius.display_name} for corruption in office"
    game.votes_yea = 20
    game.votes_nay = 5
    game.save()

    cornelius.add_status_item(Senator.StatusItem.ACCUSED)
    cornelius.save()
    scipio.add_status_item(Senator.StatusItem.PROSECUTOR)
    scipio.save()
    _setup_all_factions_done(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    scipio.refresh_from_db()
    assert cornelius.influence == 2
    assert not cornelius.has_title(Senator.Title.PRIOR_CONSUL)
    assert len(cornelius.concessions) == 0
    assert scipio.has_title(Senator.Title.PRIOR_CONSUL)
    assert scipio.influence == prosecutor_influence_before + 3
