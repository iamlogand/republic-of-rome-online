import pytest
from rorapp.actions.accept_governorship import AcceptGovernorshipAction
from rorapp.actions.nominate_governor import NominateGovernorAction
from rorapp.actions.refuse_governorship import RefuseGovernorshipAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Province, Senator


def _setup_recall(game: Game):
    senators = list(Senator.objects.filter(game=game, alive=True).order_by("id"))
    presiding_magistrate, returned, governor = senators[0], senators[4], senators[1]
    governor.location = "Sicilia"
    governor.save()
    returned.add_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
    returned.save()
    province = Province.objects.create(
        game=game, name="Sicilia", developed=False, governor=governor, term=2
    )
    assert presiding_magistrate.faction_id is not None
    faction = Faction.objects.get(id=presiding_magistrate.faction_id)
    return faction, province, returned


def _nominate(game: Game, faction: Faction, province: Province, senator: Senator):
    result = NominateGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province.id, "Governor": senator.id},
        FakeRandomResolver(),
    )
    assert result.success


def _returned_faction(senator: Senator) -> Faction:
    assert senator.faction_id is not None
    return Faction.objects.get(id=senator.faction_id)


@pytest.mark.parametrize("other_candidate_remains", [True, False])
@pytest.mark.django_db
def test_returned_governor_consent_required_only_while_another_candidate_remains(
    senate_game: Game, other_candidate_remains: bool
):
    # Arrange
    game = senate_game
    faction, province, returned = _setup_recall(game)
    if not other_candidate_remains:
        for senator in Senator.objects.filter(game=game, location="Rome"):
            senator.add_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
            senator.save()

    # Act
    _nominate(game, faction, province, returned)
    execute_effects_and_manage_actions(game.id)

    # Assert
    returned.refresh_from_db()
    assert (
        returned.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
        is other_candidate_remains
    )
    action_names = {a.name for a in AvailableAction.objects.filter(game=game)}
    assert ("Accept governorship" in action_names) is other_candidate_remains


@pytest.mark.django_db
def test_returned_governor_who_accepts_is_elected(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    faction, province, returned = _setup_recall(game)
    _nominate(game, faction, province, returned)
    accepted = AcceptGovernorshipAction().execute(
        game.id, _returned_faction(returned).id, {}, resolver
    )
    game.refresh_from_db()
    game.votes_yea = 15
    game.save()
    for f in Faction.objects.filter(game=game):
        f.add_status_item(FactionStatusItem.DONE)
        f.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert accepted.success
    province.refresh_from_db()
    assert province.governor_id == returned.id


@pytest.mark.django_db
def test_returned_governor_who_refuses_withdraws_the_proposal_without_defeat(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    faction, province, returned = _setup_recall(game)
    _nominate(game, faction, province, returned)
    game.refresh_from_db()
    proposal = game.current_proposal

    # Act
    result = RefuseGovernorshipAction().execute(
        game.id, _returned_faction(returned).id, {}, resolver
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    returned.refresh_from_db()
    assert game.current_proposal is None
    assert proposal not in game.defeated_proposals
    assert not returned.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)


@pytest.mark.django_db
def test_unaligned_returned_governor_not_offered_while_another_candidate_remains(
    senate_game: Game,
):
    # Arrange
    game = senate_game
    faction, _, returned = _setup_recall(game)
    returned.faction = None
    returned.save()

    # Act
    actions = NominateGovernorAction().get_schema(
        GameStateSnapshot(game.id), faction.id
    )

    # Assert
    options = next(
        f for f in actions[0].field_descriptors if f["name"] == "Governor"
    )["options"]
    assert returned.id not in {o["id"] for o in options}
