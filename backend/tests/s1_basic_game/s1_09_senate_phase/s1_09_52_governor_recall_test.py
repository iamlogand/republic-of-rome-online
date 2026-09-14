import pytest
from rorapp.actions.nominate_governor import NominateGovernorAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Province, Senator


def _setup_governed_province(game: Game, elected_this_turn: bool = False):
    senators = list(Senator.objects.filter(game=game, alive=True).order_by("id"))
    presiding_magistrate, candidate, governor = senators[0], senators[1], senators[4]
    governor.location = "Sicilia"
    governor.save()
    province = Province.objects.create(
        game=game,
        name="Sicilia",
        developed=False,
        governor=governor,
        term=2,
        elected_this_turn=elected_this_turn,
    )
    assert presiding_magistrate.faction_id is not None
    faction = Faction.objects.get(id=presiding_magistrate.faction_id)
    return faction, province, candidate, governor


@pytest.mark.parametrize("elected_this_turn", [False, True])
@pytest.mark.django_db
def test_governor_may_be_recalled_unless_elected_this_turn(
    senate_game: Game, elected_this_turn: bool
):
    # Arrange
    faction, _, _, _ = _setup_governed_province(senate_game, elected_this_turn)

    # Act
    actions = NominateGovernorAction().get_schema(
        GameStateSnapshot(senate_game.id), faction.id
    )

    # Assert
    assert bool(actions) is not elected_this_turn


@pytest.mark.django_db
def test_electing_a_new_governor_recalls_the_current_one(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    faction, province, candidate, governor = _setup_governed_province(game)
    result = NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province.id, "Governor": candidate.id},
        resolver,
    )
    assert result.success
    game.refresh_from_db()
    game.votes_yea = 15
    game.save()
    for f in Faction.objects.filter(game=game):
        f.add_status_item(FactionStatusItem.DONE)
        f.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    province.refresh_from_db()
    candidate.refresh_from_db()
    governor.refresh_from_db()
    assert province.governor_id == candidate.id
    assert province.term == 3
    assert candidate.location == "Sicilia"
    assert governor.location == "Rome"
    assert governor.has_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_recall_may_be_grouped_with_a_vacant_province_election(senate_game: Game):
    # Arrange
    game = senate_game
    game.sub_phase = Game.SubPhase.GOVERNOR_ELECTION
    game.save()
    faction, sicilia, _, _ = _setup_governed_province(game)
    macedonia = Province.objects.create(game=game, name="Macedonia", developed=True)

    # Act
    actions = NominateGovernorAction().get_schema(
        GameStateSnapshot(game.id), faction.id
    )

    # Assert
    assert len(actions) == 1
    provinces_field = next(
        f for f in actions[0].field_descriptors if f["name"] == "Provinces"
    )
    assert {o["id"] for o in provinces_field["options"]} == {sicilia.id, macedonia.id}
