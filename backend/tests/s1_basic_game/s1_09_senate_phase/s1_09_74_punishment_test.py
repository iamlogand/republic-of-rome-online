import pytest
from rorapp.actions.attempt_assassination import AttemptAssassinationAction
from rorapp.actions.vote_call_faction import CallFactionToVoteAction
from rorapp.actions.vote_nay import VoteNayAction
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.special_major_prosecution import (
    special_major_prosecution_proposal,
)
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


def _setup_caught_assassin(
    game: Game,
    assassin: Senator,
    target: Senator,
    roll_result: int = 1,
):
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = roll_result
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    assassin.add_status_item(Senator.StatusItem.ASSASSIN)
    assassin.add_status_item(Senator.StatusItem.CAUGHT)
    assassin.save()
    target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    target.save()


def _setup_special_prosecution(
    game: Game,
    resolver: FakeRandomResolver,
    target_popularity: int = 0,
):
    # Fabius of the first faction is caught trying to assassinate Claudius, so
    # his faction leader Valerius stands trial. Furius of the third is Censor.
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    furius = Senator.objects.get(game=game, family_name="Furius")

    valerius.add_title(Senator.Title.FACTION_LEADER)
    valerius.save()
    furius.add_title(Senator.Title.CENSOR)
    furius.save()
    claudius.popularity = target_popularity
    claudius.save()

    # An appeal roll of 6 leaves the vote untouched
    resolver.dice_rolls = [3, 3]
    _setup_caught_assassin(game, fabius, claudius)

    return fabius, valerius, claudius, furius


def _presiding_faction(game: Game) -> Faction:
    faction = Senator.objects.get(
        game=game, titles__contains=Senator.Title.PRESIDING_MAGISTRATE.value
    ).faction
    assert faction is not None
    return faction


def _vote(game: Game, resolver: FakeRandomResolver, yea_positions: list):
    # Run the vote to completion, with the presiding magistrate voting last
    presiding_faction = _presiding_faction(game)

    for faction in Faction.objects.filter(game=game).order_by("position"):
        if faction.id == presiding_faction.id:
            continue
        CallFactionToVoteAction().execute(
            game.id, presiding_faction.id, {"target_faction_id": faction.id}, resolver
        )
        execute_effects_and_manage_actions(game.id, resolver)
        action = (
            VoteYeaAction if faction.position in yea_positions else VoteNayAction
        )
        action().execute(game.id, faction.id, {}, resolver)
        execute_effects_and_manage_actions(game.id, resolver)

    action = (
        VoteYeaAction if presiding_faction.position in yea_positions else VoteNayAction
    )
    action().execute(game.id, presiding_faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)


def _attempt_assassination(
    game: Game,
    resolver: FakeRandomResolver,
    assassin: Senator,
    target: Senator,
    roll: int,
):
    faction_id = assassin.faction_id
    assert faction_id is not None
    resolver.dice_rolls = [roll] + resolver.dice_rolls
    AttemptAssassinationAction().execute(
        game.id,
        faction_id,
        {"Assassin": assassin.id, "Target": target.id, "Assassin cards": 0},
        resolver,
    )
    execute_effects_and_manage_actions(game.id, resolver)


def _trial_from_attempt(game: Game, resolver: FakeRandomResolver):
    # The same trial as _setup_special_prosecution, opened through the action so
    # that the per-turn assassination limits are set as they are in a real game
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    furius = Senator.objects.get(game=game, family_name="Furius")

    valerius.add_title(Senator.Title.FACTION_LEADER)
    valerius.save()
    furius.add_title(Senator.Title.CENSOR)
    furius.save()

    # An appeal roll of 6 leaves the vote untouched
    resolver.dice_rolls = [3, 3]
    _attempt_assassination(game, resolver, fabius, claudius, roll=1)

    return fabius, valerius, claudius, furius


@pytest.mark.django_db
def test_caught_assassin_is_killed(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_caught_assassin(game, cornelius, claudius)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert not cornelius.alive


@pytest.mark.django_db
def test_caught_assassin_who_is_faction_leader_leaves_no_heir(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    cornelius.add_title(Senator.Title.FACTION_LEADER)
    cornelius.save()
    _setup_caught_assassin(game, cornelius, claudius)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert not cornelius.alive
    assert cornelius.generation == 1
    assert cornelius.faction is None


@pytest.mark.django_db
def test_caught_assassin_who_is_faction_leader_faces_no_prosecution(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    cornelius.add_title(Senator.Title.FACTION_LEADER)
    cornelius.save()
    _setup_caught_assassin(game, cornelius, claudius)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_caught_assassin_who_is_faction_leader_implicates_faction_members(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    cornelius.add_title(Senator.Title.FACTION_LEADER)
    cornelius.save()
    claudius.popularity = 2
    claudius.save()
    resolver.mortality_chits = [[valerius.code]]
    _setup_caught_assassin(game, cornelius, claudius)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    valerius.refresh_from_db()
    assert not valerius.alive


@pytest.mark.django_db
def test_faction_leader_of_caught_assassin_loses_5_influence(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    fabius, valerius, _, _ = _setup_special_prosecution(game, resolver)
    influence_before = valerius.influence

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    valerius.refresh_from_db()
    assert valerius.influence == influence_before - 5


@pytest.mark.django_db
def test_faction_leader_in_rome_is_put_on_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, claudius, _ = _setup_special_prosecution(game, resolver)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    valerius.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPECIAL_MAJOR_PROSECUTION
    assert game.current_proposal == (
        f"Prosecute {valerius.display_name} for the attempted assassination of "
        f"{claudius.display_name}"
    )
    assert valerius.has_status_item(Senator.StatusItem.ACCUSED)


@pytest.mark.django_db
def test_faction_leader_away_from_rome_is_not_put_on_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, _ = _setup_special_prosecution(game, resolver)
    valerius.location = "Sicilia"
    valerius.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    valerius.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert valerius.influence == 0


@pytest.mark.django_db
def test_censor_presides_over_the_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, _, _, furius = _setup_special_prosecution(game, resolver)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    furius.refresh_from_db()
    assert furius.has_title(Senator.Title.PRESIDING_MAGISTRATE)


@pytest.mark.django_db
def test_accused_influence_counts_against_conviction(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, _ = _setup_special_prosecution(game, resolver)
    valerius.influence = 9
    valerius.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.votes_nay == 4


@pytest.mark.django_db
def test_trial_cannot_be_vetoed(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    _setup_special_prosecution(game, resolver)
    for faction in Faction.objects.filter(game=game):
        faction.cards = ["tribune"]
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert not AvailableAction.objects.filter(
        game=game, base_name="Veto with tribune"
    ).exists()


@pytest.mark.django_db
def test_guilty_verdict_kills_the_faction_leader_without_an_heir(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, _ = _setup_special_prosecution(game, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    _vote(game, resolver, yea_positions=[2, 3])

    # Assert
    valerius.refresh_from_db()
    assert not valerius.alive
    assert valerius.generation == 1
    assert valerius.faction is None


@pytest.mark.django_db
def test_guilty_verdict_implicates_faction_members_in_rome(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _setup_special_prosecution(game, resolver, target_popularity=2)
    julius = Senator.objects.get(game=game, family_name="Julius")
    resolver.mortality_chits = [[julius.code]]
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    _vote(game, resolver, yea_positions=[2, 3])

    # Assert
    julius.refresh_from_db()
    assert not julius.alive


@pytest.mark.django_db
def test_acquittal_leaves_the_faction_leader_alive(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, _ = _setup_special_prosecution(game, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    _vote(game, resolver, yea_positions=[])

    # Assert
    valerius.refresh_from_db()
    assert valerius.alive


@pytest.mark.django_db
def test_appeal_is_modified_by_the_popularity_of_the_target(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _setup_special_prosecution(game, resolver, target_popularity=-3)
    execute_effects_and_manage_actions(game.id, resolver)
    presiding_faction = _presiding_faction(game)
    accused_faction = Senator.objects.get(game=game, family_name="Valerius").faction
    assert accused_faction is not None
    game.refresh_from_db()
    votes_nay_before = game.votes_nay

    # Act
    CallFactionToVoteAction().execute(
        game.id,
        presiding_faction.id,
        {"target_faction_id": accused_faction.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert — a roll of 6 against a target popularity of −3 gives a result of 9
    game.refresh_from_db()
    assert game.votes_nay == votes_nay_before + 5


@pytest.mark.django_db
def test_suspended_proposal_resumes_after_the_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _setup_special_prosecution(game, resolver)
    game.current_proposal = "Raise 2 legions"
    game.votes_yea = 4
    game.votes_nay = 1
    game.save()
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    _vote(game, resolver, yea_positions=[])

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert game.current_proposal == "Raise 2 legions"
    assert game.votes_yea == 4
    assert game.votes_nay == 1


@pytest.mark.django_db
def test_presiding_magistrate_returns_after_the_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    _setup_special_prosecution(game, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    _vote(game, resolver, yea_positions=[])

    # Assert
    cornelius.refresh_from_db()
    assert cornelius.has_title(Senator.Title.PRESIDING_MAGISTRATE)


@pytest.mark.django_db
def test_mob_kills_the_accused_on_a_deadly_appeal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, _ = _setup_special_prosecution(game, resolver, target_popularity=9)
    resolver.dice_rolls = [1, 1]
    execute_effects_and_manage_actions(game.id, resolver)
    presiding_faction = _presiding_faction(game)
    accused_faction = valerius.faction
    assert accused_faction is not None

    # Act
    CallFactionToVoteAction().execute(
        game.id,
        presiding_faction.id,
        {"target_faction_id": accused_faction.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    valerius.refresh_from_db()
    assert not valerius.alive
    assert valerius.generation == 1
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_crowd_frees_the_accused_on_a_favourable_appeal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, _ = _setup_special_prosecution(game, resolver, target_popularity=-9)
    resolver.dice_rolls = [2, 1]
    execute_effects_and_manage_actions(game.id, resolver)
    presiding_faction = _presiding_faction(game)
    accused_faction = valerius.faction
    assert accused_faction is not None

    # Act
    CallFactionToVoteAction().execute(
        game.id,
        presiding_faction.id,
        {"target_faction_id": accused_faction.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    valerius.refresh_from_db()
    assert valerius.alive
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_suspended_proposal_is_cancelled_when_the_mob_kills_a_named_senator(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, _ = _setup_special_prosecution(game, resolver, target_popularity=9)
    valerius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    valerius.save()
    game.current_proposal = "Raise 2 legions"
    game.save()
    resolver.dice_rolls = [1, 1]
    execute_effects_and_manage_actions(game.id, resolver)
    presiding_faction = _presiding_faction(game)
    accused_faction = valerius.faction
    assert accused_faction is not None

    # Act
    CallFactionToVoteAction().execute(
        game.id,
        presiding_faction.id,
        {"target_faction_id": accused_faction.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.current_proposal is None


@pytest.mark.django_db
def test_suspended_proposal_is_cancelled_when_the_mob_kills_the_censor(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, furius = _setup_special_prosecution(
        game, resolver, target_popularity=-9
    )
    furius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    furius.save()
    game.current_proposal = "Raise 2 legions"
    game.save()
    resolver.dice_rolls = [2, 1]
    resolver.mortality_chits = [[furius.code]]
    execute_effects_and_manage_actions(game.id, resolver)
    presiding_faction = _presiding_faction(game)
    accused_faction = valerius.faction
    assert accused_faction is not None

    # Act
    CallFactionToVoteAction().execute(
        game.id,
        presiding_faction.id,
        {"target_faction_id": accused_faction.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    furius.refresh_from_db()
    game.refresh_from_db()
    assert not furius.alive
    assert game.current_proposal is None


@pytest.mark.django_db
def test_conviction_does_not_cancel_a_proposal_that_did_not_name_the_accused(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, _ = _setup_special_prosecution(game, resolver)
    game.current_proposal = "Raise 2 legions"
    game.save()
    execute_effects_and_manage_actions(game.id, resolver)
    valerius.refresh_from_db()
    valerius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    valerius.save()

    # Act
    _vote(game, resolver, yea_positions=[2, 3])

    # Assert
    game.refresh_from_db()
    valerius.refresh_from_db()
    assert not valerius.alive
    assert game.current_proposal == "Raise 2 legions"


@pytest.mark.django_db
def test_heir_does_not_inherit_the_suspended_role_of_a_senator_killed_by_the_mob(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, valerius, _, furius = _setup_special_prosecution(
        game, resolver, target_popularity=-9
    )
    furius.add_title(Senator.Title.FACTION_LEADER)
    furius.add_status_item(Senator.StatusItem.CORRUPT)
    furius.save()
    game.current_proposal = "Raise 2 legions"
    game.save()
    resolver.dice_rolls = [2, 1]
    resolver.mortality_chits = [[furius.code]]
    execute_effects_and_manage_actions(game.id, resolver)
    presiding_faction = _presiding_faction(game)
    accused_faction = valerius.faction
    assert accused_faction is not None

    # Act
    CallFactionToVoteAction().execute(
        game.id,
        presiding_faction.id,
        {"target_faction_id": accused_faction.id},
        resolver,
    )
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    furius.refresh_from_db()
    assert furius.alive
    assert furius.generation == 2
    assert not furius.has_status_item(Senator.StatusItem.CORRUPT)


@pytest.mark.django_db
def test_gavel_passes_to_the_hrao_when_the_previous_magistrate_dies_in_the_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, _, _, furius = _setup_special_prosecution(game, resolver, target_popularity=2)
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    manlius.add_title(Senator.Title.FIELD_CONSUL)
    manlius.save()
    resolver.mortality_chits = [[cornelius.code]]
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    _vote(game, resolver, yea_positions=[2, 3])

    # Assert
    cornelius.refresh_from_db()
    furius.refresh_from_db()
    manlius.refresh_from_db()
    assert not cornelius.alive
    assert not furius.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    assert manlius.has_title(Senator.Title.PRESIDING_MAGISTRATE)


@pytest.mark.django_db
def test_assassination_may_be_attempted_during_a_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _trial_from_attempt(game, resolver)
    junius = Senator.objects.get(game=game, family_name="Junius")
    assert junius.faction_id is not None

    # Act
    allowed = AttemptAssassinationAction().is_allowed(
        GameStateSnapshot(game.id), junius.faction_id
    )

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPECIAL_MAJOR_PROSECUTION
    assert allowed is not None


@pytest.mark.django_db
def test_faction_that_already_attempted_cannot_attempt_again_during_a_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    fabius, _, _, _ = _trial_from_attempt(game, resolver)

    # Act
    allowed = AttemptAssassinationAction().is_allowed(
        GameStateSnapshot(game.id), fabius.faction_id
    )

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_faction_already_targeted_cannot_be_targeted_again_during_a_trial(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _trial_from_attempt(game, resolver)
    junius = Senator.objects.get(game=game, family_name="Junius")
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    assert junius.faction_id is not None

    # Act
    result = AttemptAssassinationAction().execute(
        game.id,
        junius.faction_id,
        {"Assassin": junius.id, "Target": manlius.id, "Assassin cards": 0},
        resolver,
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_trial_resumes_after_an_assassination_interrupts_it(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Raise 2 legions"
    game.save()
    _, valerius, claudius, _ = _trial_from_attempt(game, resolver)
    junius = Senator.objects.get(game=game, family_name="Junius")
    julius = Senator.objects.get(game=game, family_name="Julius")

    # Act
    _attempt_assassination(game, resolver, junius, julius, roll=3)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPECIAL_MAJOR_PROSECUTION
    assert game.current_proposal == special_major_prosecution_proposal(
        valerius.display_name, claudius.display_name
    )
    assert game.interrupted_sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_second_caught_assassin_is_tried_after_the_first(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Raise 2 legions"
    game.save()
    aurelius = Senator.objects.get(game=game, family_name="Aurelius")
    aurelius.add_title(Senator.Title.FACTION_LEADER)
    aurelius.save()
    _, valerius, claudius, _ = _trial_from_attempt(game, resolver)
    junius = Senator.objects.get(game=game, family_name="Junius")
    julius = Senator.objects.get(game=game, family_name="Julius")
    _attempt_assassination(game, resolver, junius, julius, roll=1)

    game.refresh_from_db()
    assert game.current_proposal == special_major_prosecution_proposal(
        valerius.display_name, claudius.display_name
    )
    assert Log.objects.filter(
        game=game,
        text=(
            f"{aurelius.display_name} will stand trial for the attempted "
            f"assassination of {julius.display_name} once the senate has "
            f"finished with {valerius.display_name}."
        ),
    ).exists()

    # Act
    # Two appeal rolls each, since the second trial opens as the first concludes
    resolver.dice_rolls = [3, 3, 3, 3]
    _vote(game, resolver, yea_positions=[])

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPECIAL_MAJOR_PROSECUTION
    assert game.current_proposal == special_major_prosecution_proposal(
        aurelius.display_name, julius.display_name
    )

    # Act
    _vote(game, resolver, yea_positions=[])

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert game.current_proposal == "Raise 2 legions"
    assert game.special_major_prosecutions == []


@pytest.mark.django_db
def test_trial_is_abandoned_when_the_accused_is_assassinated(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Raise 2 legions"
    game.save()
    _, valerius, claudius, _ = _trial_from_attempt(game, resolver)
    accused_name = valerius.display_name
    junius = Senator.objects.get(game=game, family_name="Junius")

    # Act
    _attempt_assassination(game, resolver, junius, valerius, roll=5)

    # Assert
    game.refresh_from_db()
    valerius.refresh_from_db()
    assert valerius.generation == 2
    assert Log.objects.filter(
        game=game, text=f"The prosecution of {accused_name} was cancelled."
    ).exists()
    assert game.special_major_prosecutions == []
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert game.current_proposal == "Raise 2 legions"


@pytest.mark.django_db
def test_queued_trial_is_abandoned_when_its_accused_is_assassinated(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Raise 2 legions"
    game.save()
    aurelius = Senator.objects.get(game=game, family_name="Aurelius")
    aurelius.add_title(Senator.Title.FACTION_LEADER)
    aurelius.save()
    _trial_from_attempt(game, resolver)
    junius = Senator.objects.get(game=game, family_name="Junius")
    julius = Senator.objects.get(game=game, family_name="Julius")
    _attempt_assassination(game, resolver, junius, julius, roll=1)
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    _attempt_assassination(game, resolver, manlius, aurelius, roll=5)

    # Act
    _vote(game, resolver, yea_positions=[])

    # Assert
    game.refresh_from_db()
    aurelius.refresh_from_db()
    assert aurelius.generation == 2
    assert game.special_major_prosecutions == []
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert game.current_proposal == "Raise 2 legions"


@pytest.mark.django_db
def test_suspended_proposal_is_cancelled_when_an_assassination_kills_a_named_senator(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    julius.save()
    game.current_proposal = "Raise 2 legions"
    game.save()
    _trial_from_attempt(game, resolver)
    junius = Senator.objects.get(game=game, family_name="Junius")
    _attempt_assassination(game, resolver, junius, julius, roll=5)

    # Act
    _vote(game, resolver, yea_positions=[])

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert game.current_proposal is None
