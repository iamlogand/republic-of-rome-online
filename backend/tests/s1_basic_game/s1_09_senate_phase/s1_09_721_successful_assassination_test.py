import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


def _setup_resolve(
    game: Game,
    assassin: Senator,
    target: Senator,
    roll_result: int,
    interrupted_sub_phase: str = Game.SubPhase.OTHER_BUSINESS,
):
    """Set up game state for ResolveAssassinationEffect to fire immediately."""
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = roll_result
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = interrupted_sub_phase
    game.save()
    assassin.add_status_item(Senator.StatusItem.ASSASSIN)
    assassin.save()
    target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    target.save()


@pytest.mark.django_db
def test_successful_assassination_kills_target(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_resolve(game, cornelius, claudius, roll_result=5)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    claudius.refresh_from_db()
    assert not claudius.alive


@pytest.mark.django_db
def test_pm_title_transfers_to_hrao_when_pm_is_killed(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = 5
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.add_title(Senator.Title.ROME_CONSUL)
    claudius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    claudius.add_title(Senator.Title.HRAO)
    claudius.save()
    cornelius.add_status_item(Senator.StatusItem.ASSASSIN)
    cornelius.save()
    claudius.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    claudius.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    claudius.refresh_from_db()
    cornelius.refresh_from_db()
    assert not claudius.alive
    assert cornelius.has_title(Senator.Title.PRESIDING_MAGISTRATE)


@pytest.mark.django_db
def test_killing_consul_nominee_clears_proposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls: Claudius and Fabius"
    game.interrupted_sub_phase = Game.SubPhase.CONSULAR_ELECTION
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    claudius.save()
    _setup_resolve(
        game,
        cornelius,
        claudius,
        roll_result=5,
        interrupted_sub_phase=Game.SubPhase.CONSULAR_ELECTION,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert not game.current_proposal
    assert game.sub_phase == Game.SubPhase.CONSULAR_ELECTION


@pytest.mark.django_db
def test_killing_prosecutor_clears_proposal_and_decrements_count(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Prosecute Fabius for corruption"
    game.prosecutions_remaining = 2
    game.interrupted_sub_phase = Game.SubPhase.PROSECUTION
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    claudius.save()
    _setup_resolve(
        game,
        cornelius,
        claudius,
        roll_result=5,
        interrupted_sub_phase=Game.SubPhase.PROSECUTION,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert not game.current_proposal
    assert game.prosecutions_remaining == 1
    assert game.sub_phase == Game.SubPhase.PROSECUTION


@pytest.mark.django_db
def test_killing_concession_recipient_clears_proposal_and_blocks_reproposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Award the Grain Concession concession to Claudius"
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    claudius.save()
    _setup_resolve(
        game,
        cornelius,
        claudius,
        roll_result=5,
        interrupted_sub_phase=Game.SubPhase.OTHER_BUSINESS,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert not game.current_proposal
    assert game.has_unavailable_proposal(
        "Award the Grain Concession concession to Claudius"
    )


@pytest.mark.django_db
def test_land_bill_proposal_not_cleared_when_sponsor_killed(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    land_bill_proposal = (
        "Pass type II land bill sponsored by Claudius and co-sponsored by Manlius"
    )
    game.current_proposal = land_bill_proposal
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    claudius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    claudius.save()
    _setup_resolve(
        game,
        cornelius,
        claudius,
        roll_result=5,
        interrupted_sub_phase=Game.SubPhase.OTHER_BUSINESS,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == land_bill_proposal


@pytest.mark.django_db
def test_killing_senator_not_named_in_proposal_has_no_proposal_consequence(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Deploy forces"
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_resolve(
        game,
        cornelius,
        claudius,
        roll_result=5,
        interrupted_sub_phase=Game.SubPhase.OTHER_BUSINESS,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == "Deploy forces"
