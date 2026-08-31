from typing import List
import pytest
from rorapp.actions.propose_disbanding_forces import ProposeDisbandingForcesAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Fleet, Game, Legion, Senator


def _pass_proposal(game: Game, proposal: str, resolver: FakeRandomResolver, yea: int = 15, nay: int = 0):
    game.refresh_from_db()
    game.current_proposal = proposal
    game.votes_yea = yea
    game.votes_nay = nay
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    execute_effects_and_manage_actions(game.id, resolver)


def _create_reserve_legions(game: Game, numbers: List[int]) -> List[Legion]:
    return [
        Legion.objects.create(game=game, number=n, recently_raised=False)
        for n in numbers
    ]


def _presiding_magistrate_faction_id(game: Game) -> int:
    senator = next(
        s
        for s in Senator.objects.filter(game=game)
        if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )
    return senator.faction_id


@pytest.mark.django_db
def test_legions_and_fleets_are_removed_when_proposal_passes(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    _create_reserve_legions(game, [1, 2, 3])
    Fleet.objects.create(game=game, number=1, recently_raised=False)

    # Act
    _pass_proposal(game, "Disband 2 legions (I, II) and 1 fleet (I)", resolver)

    # Assert
    assert list(Legion.objects.filter(game=game).values_list("number", flat=True)) == [3]
    assert Fleet.objects.filter(game=game).count() == 0


@pytest.mark.django_db
def test_forces_survive_when_proposal_is_defeated(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    _create_reserve_legions(game, [1, 2])

    # Act
    _pass_proposal(game, "Disband 2 legions (I, II)", resolver, yea=0, nay=15)

    # Assert
    game.refresh_from_db()
    assert Legion.objects.filter(game=game).count() == 2
    assert game.has_defeated_proposal("Disband 2 legions (I, II)")


@pytest.mark.django_db
def test_disbanded_legions_cannot_be_rebuilt_in_the_same_senate_phase(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    game.state_treasury = 100
    game.save()
    _create_reserve_legions(game, [1, 2])
    _pass_proposal(game, "Disband 2 legions (I, II)", resolver)

    # Act
    _pass_proposal(game, "Raise 2 legions", resolver)

    # Assert
    assert list(Legion.objects.filter(game=game).values_list("number", flat=True)) == [3, 4]


@pytest.mark.django_db
def test_forces_raised_this_senate_phase_cannot_be_disbanded(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    game.state_treasury = 100
    game.save()
    _pass_proposal(game, "Raise 1 legion", resolver)
    legion = Legion.objects.get(game=game)
    faction = game.factions.first()

    # Act
    result = ProposeDisbandingForcesAction().execute(
        game.id, faction.id, {"Legions": [legion.id], "Fleets": []}, resolver
    )

    # Assert
    assert result.success is False
    assert Legion.objects.filter(game=game).count() == 1


@pytest.mark.django_db
def test_deployed_forces_cannot_be_disbanded(proconsul_campaign: Game, resolver: FakeRandomResolver):
    # Arrange
    game = proconsul_campaign
    legion = Legion.objects.create(game=game, number=1)
    legion.campaign = Campaign.objects.get(game=game)
    legion.save()
    faction = game.factions.first()
    assert faction is not None

    # Act
    result = ProposeDisbandingForcesAction().execute(
        game.id, faction.id, {"Legions": [legion.id], "Fleets": []}, resolver
    )

    # Assert
    assert result.success is False
    assert Legion.objects.filter(game=game).count() == 1


@pytest.mark.django_db
def test_proposal_names_the_selected_forces(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    legions = _create_reserve_legions(game, [1, 2, 3])
    fleet = Fleet.objects.create(game=game, number=4, recently_raised=False)
    faction_id = _presiding_magistrate_faction_id(game)

    # Act
    ProposeDisbandingForcesAction().execute(
        game.id,
        faction_id,
        {"Legions": [l.id for l in legions], "Fleets": [fleet.id]},
        resolver,
    )

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == "Disband 3 legions (I–III) and 1 fleet (IV)"


@pytest.mark.django_db
def test_only_reserve_forces_are_offered_for_disbandment(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    reserve_legion = Legion.objects.create(game=game, number=1, recently_raised=False)
    deployed_legion = Legion.objects.create(game=game, number=2)
    deployed_legion.campaign = Campaign.objects.get(game=game)
    deployed_legion.save()
    faction_id = _presiding_magistrate_faction_id(game)

    # Act
    actions = ProposeDisbandingForcesAction().get_schema(
        GameStateSnapshot(game.id), faction_id
    )

    # Assert
    legion_options = actions[0].field_descriptors[0]["options"]
    assert [option["id"] for option in legion_options] == [reserve_legion.id]


@pytest.mark.django_db
def test_disbanding_forces_is_unavailable_without_reserve_forces(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    deployed_legion = Legion.objects.create(game=game, number=1)
    deployed_legion.campaign = Campaign.objects.get(game=game)
    deployed_legion.save()
    faction_id = _presiding_magistrate_faction_id(game)

    # Act
    faction = ProposeDisbandingForcesAction().is_allowed(
        GameStateSnapshot(game.id), faction_id
    )

    # Assert
    assert faction is None


@pytest.mark.django_db
def test_recruitment_restrictions_are_lifted_when_the_senate_phase_ends(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    game.state_treasury = 100
    game.save()
    _create_reserve_legions(game, [1])
    _pass_proposal(game, "Disband 1 legion (I)", resolver)
    _pass_proposal(game, "Raise 1 legion", resolver)

    # Act
    game.refresh_from_db()
    game.sub_phase = Game.SubPhase.END
    game.save()
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.disbanded_legion_numbers == []
    assert not Legion.objects.filter(game=game, recently_raised=True).exists()
