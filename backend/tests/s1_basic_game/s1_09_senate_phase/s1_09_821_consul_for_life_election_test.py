import pytest
from rorapp.actions.advanced_vote import AdvancedVoteAction
from rorapp.actions.nominate_consul_for_life import NominateConsulForLifeAction
from rorapp.actions.veto_with_tribune import VetoWithTribuneAction
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.assassination_proposal_consequences import (
    handle_proposal_consequences,
)
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.models import Game, Senator


def _presiding_magistrate(game: Game) -> Senator:
    return next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )


def _make_candidate(game: Game, influence: int = 21) -> Senator:
    senator = next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if not s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )
    senator.influence = influence
    senator.save()
    return senator


def _candidate_ids(game: Game, faction_id: int) -> list:
    snapshot = GameStateSnapshot(game.id)
    actions = NominateConsulForLifeAction().get_schema(snapshot, faction_id)
    return [o["id"] for o in actions[0].field_descriptors[0]["options"]]


@pytest.mark.parametrize(
    "sub_phase",
    [
        Game.SubPhase.OTHER_BUSINESS,
        Game.SubPhase.CENSOR_ELECTION,
        Game.SubPhase.DICTATOR_ELECTION,
    ],
)
@pytest.mark.django_db
def test_presiding_magistrate_can_nominate_after_consular_elections(
    senate_game: Game, sub_phase
):
    # Arrange
    game = senate_game
    game.sub_phase = sub_phase
    game.save()
    _make_candidate(game)
    pm_faction = _presiding_magistrate(game).faction
    assert pm_faction is not None

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), pm_faction.id
    )

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_nomination_not_allowed_during_prosecution(senate_game: Game):
    # Arrange
    game = senate_game
    game.sub_phase = Game.SubPhase.PROSECUTION
    game.save()
    _make_candidate(game)
    pm_faction = _presiding_magistrate(game).faction
    assert pm_faction is not None

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), pm_faction.id
    )

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_senator_below_21_influence_is_not_a_candidate(senate_game: Game):
    # Arrange
    game = senate_game
    Senator.objects.filter(game=game).update(influence=20)
    pm = _presiding_magistrate(game)
    assert pm.faction is not None

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), pm.faction.id
    )

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_senator_with_21_influence_is_a_candidate(senate_game: Game):
    # Arrange
    game = senate_game
    Senator.objects.filter(game=game).update(influence=1)
    candidate = _make_candidate(game, influence=21)
    pm = _presiding_magistrate(game)
    assert pm.faction is not None

    # Act
    candidate_ids = _candidate_ids(game, pm.faction.id)

    # Assert
    assert candidate_ids == [candidate.id]


@pytest.mark.django_db
def test_sitting_consul_is_a_candidate(senate_game: Game):
    # Arrange
    game = senate_game
    Senator.objects.filter(game=game).update(influence=1)
    pm = _presiding_magistrate(game)
    pm.influence = 21
    pm.save()
    assert pm.faction is not None

    # Act
    candidate_ids = _candidate_ids(game, pm.faction.id)

    # Assert
    assert pm.has_title(Senator.Title.ROME_CONSUL)
    assert candidate_ids == [pm.id]


@pytest.mark.django_db
def test_senator_outside_rome_is_not_a_candidate(senate_game: Game):
    # Arrange
    game = senate_game
    Senator.objects.filter(game=game).update(influence=1)
    candidate = _make_candidate(game, influence=21)
    candidate.location = "Sicilia"
    candidate.save()
    pm = _presiding_magistrate(game)
    assert pm.faction is not None

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), pm.faction.id
    )

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_passed_vote_grants_consul_for_life(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.votes_yea = 20
    game.votes_nay = 0
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    candidate.refresh_from_db()
    assert candidate.has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_consul_for_life_gains_no_influence_and_no_offices(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    previous_hrao = _presiding_magistrate(game)
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.votes_yea = 20
    game.votes_nay = 0
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    candidate.refresh_from_db()
    previous_hrao.refresh_from_db()
    assert candidate.influence == 21
    assert not candidate.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    assert not candidate.has_title(Senator.Title.HRAO)
    assert previous_hrao.has_title(Senator.Title.HRAO)


@pytest.mark.django_db
def test_failed_vote_does_not_grant_consul_for_life(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.votes_yea = 0
    game.votes_nay = 20
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    candidate.refresh_from_db()
    assert not candidate.has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_nominee_adds_his_influence_to_his_vote_total(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    faction = candidate.faction
    assert faction is not None
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.save()
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    candidate.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    candidate.save()
    base_votes = sum(
        s.votes for s in Senator.objects.filter(game=game, faction=faction)
    )

    # Act
    VoteYeaAction().execute(game.id, faction.id, {}, resolver)

    # Assert
    game.refresh_from_db()
    assert game.votes_yea == base_votes + candidate.influence


@pytest.mark.django_db
def test_nominee_adds_his_influence_when_voting_nay_by_advanced_vote(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    faction = candidate.faction
    assert faction is not None
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.save()
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    candidate.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    candidate.save()
    faction_senators = list(Senator.objects.filter(game=game, faction=faction))
    selection = {
        "senator_votes": {
            str(s.id): {
                "decision": "nay" if s.id == candidate.id else "abstain",
                "bought_votes": 0,
            }
            for s in faction_senators
        }
    }

    # Act
    AdvancedVoteAction().execute(game.id, faction.id, selection, resolver)

    # Assert
    game.refresh_from_db()
    assert game.votes_nay == candidate.votes + candidate.influence


@pytest.mark.django_db
def test_nomination_unavailable_for_rest_of_turn_after_proposing(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    pm_faction = _presiding_magistrate(game).faction
    assert pm_faction is not None
    NominateConsulForLifeAction().execute(
        game.id, pm_faction.id, {"Consul for Life": candidate.id}, resolver
    )
    game.refresh_from_db()
    game.votes_yea = 0
    game.votes_nay = 20
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), pm_faction.id
    )

    # Assert
    game.refresh_from_db()
    assert game.consul_for_life_proposed
    assert allowed is None


@pytest.mark.django_db
def test_nomination_lock_is_released_at_the_end_of_the_senate_phase(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.END
    game.consul_for_life_proposed = True
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert not game.consul_for_life_proposed


@pytest.mark.django_db
def test_nomination_cannot_be_vetoed(senate_game: Game):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.save()
    pm_faction = _presiding_magistrate(game).faction
    assert pm_faction is not None
    other_faction = game.factions.exclude(id=pm_faction.id).first()
    assert other_faction is not None
    tribune_senator = Senator.objects.filter(game=game, faction=other_faction).first()
    assert tribune_senator is not None
    tribune_senator.add_status_item(Senator.StatusItem.FREE_TRIBUNE)
    tribune_senator.save()

    # Act
    allowed = VetoWithTribuneAction().is_allowed(
        GameStateSnapshot(game.id), other_faction.id
    )

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_tribune_can_nominate_consul_for_life(senate_game: Game):
    # Arrange
    game = senate_game
    _make_candidate(game)
    pm_faction = _presiding_magistrate(game).faction
    assert pm_faction is not None
    other_faction = game.factions.exclude(id=pm_faction.id).first()
    assert other_faction is not None
    other_faction.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    other_faction.save()

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), other_faction.id
    )

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_nomination_unavailable_while_a_consul_for_life_holds_the_title(
    senate_game: Game,
):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    candidate.add_title(Senator.Title.CONSUL_FOR_LIFE)
    candidate.save()
    pm_faction = _presiding_magistrate(game).faction
    assert pm_faction is not None

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), pm_faction.id
    )

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_pending_vote_count_includes_the_nominee_influence(senate_game: Game):
    # Arrange
    game = senate_game
    candidate = _make_candidate(game)
    base_pending = game.votes_pending
    game.current_proposal = f"Elect Consul for Life {candidate.display_name}"
    game.save()
    candidate.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    candidate.save()

    # Act
    pending = game.votes_pending

    # Assert
    assert pending == base_pending + candidate.influence


@pytest.mark.django_db
def test_nomination_stays_unavailable_after_the_sub_phase_moves_on(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.sub_phase = Game.SubPhase.CENSOR_ELECTION
    game.save()
    candidate = _make_candidate(game)
    pm_faction = _presiding_magistrate(game).faction
    assert pm_faction is not None
    NominateConsulForLifeAction().execute(
        game.id, pm_faction.id, {"Consul for Life": candidate.id}, resolver
    )
    game.refresh_from_db()
    game.votes_yea = 0
    game.votes_nay = 20
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    execute_effects_and_manage_actions(game.id, resolver)
    game.refresh_from_db()
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.clear_senate_sub_phase_proposals()
    game.save()

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), pm_faction.id
    )

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_nomination_stays_unavailable_after_the_nominee_is_assassinated(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.sub_phase = Game.SubPhase.CENSOR_ELECTION
    game.save()
    candidate = _make_candidate(game)
    successor = next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if s.id != candidate.id
        and not s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )
    successor.influence = 22
    successor.save()
    pm_faction = _presiding_magistrate(game).faction
    assert pm_faction is not None
    NominateConsulForLifeAction().execute(
        game.id, pm_faction.id, {"Consul for Life": candidate.id}, resolver
    )
    game.refresh_from_db()
    game.interrupted_sub_phase = Game.SubPhase.CENSOR_ELECTION
    game.save()
    kill_senator(candidate, CauseOfDeath.ASSASSINATION)
    game.refresh_from_db()
    handle_proposal_consequences(game, candidate, True)
    game.refresh_from_db()

    # Act
    allowed = NominateConsulForLifeAction().is_allowed(
        GameStateSnapshot(game.id), pm_faction.id
    )

    # Assert
    assert game.current_proposal is None
    assert allowed is None
