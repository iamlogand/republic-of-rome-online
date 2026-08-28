import pytest

from rorapp.actions.advanced_vote import AdvancedVoteAction
from rorapp.actions.attempt_assassination import AttemptAssassinationAction
from rorapp.actions.attempt_persuasion import AttemptPersuasionAction
from rorapp.actions.close_prosecutions import CloseProsecutionsAction
from rorapp.actions.close_senate import CloseSenateAction
from rorapp.actions.elect_governor import ElectGovernorAction
from rorapp.actions.play_tribune import PlayTribuneAction
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.end_prosecutions import end_prosecutions
from rorapp.helpers.governor_election import (
    format_governor_proposal,
    format_grouped_governor_proposal,
    governor_field_name,
)
from rorapp.helpers.kill_senator import kill_senator
from rorapp.helpers.senate_voting import faction_senators_attending_senate
from rorapp.models import AvailableAction, Faction, Game, Log, Province, Senator


def _setup_all_factions_done(game: Game):
    for f in Faction.objects.filter(game=game):
        f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
        f.add_status_item(FactionStatusItem.DONE)
        f.save()


def _propose_single_governor_motion(
    game: Game,
    faction: Faction,
    province: Province,
    candidate: Senator,
    *,
    string_ids: bool = False,
) -> None:
    province_sel = str(province.id) if string_ids else province.id
    governor_sel = str(candidate.id) if string_ids else candidate.id
    result = ElectGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province_sel, "Governor": governor_sel},
        FakeRandomResolver(),
    )
    assert result.success
    game.refresh_from_db()
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()
    _setup_all_factions_done(game)


def _governor_option_ids(action: AvailableAction, province_name: str) -> set[int]:
    field = next(
        f
        for f in action.field_descriptors
        if f["name"] == governor_field_name(province_name)
    )
    return {option["id"] for option in field["options"]}


def _faction_of(senator: Senator) -> Faction:
    assert senator.faction_id is not None
    return Faction.objects.get(id=senator.faction_id)


@pytest.fixture
def governor_election_game(basic_game: Game):
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.GOVERNOR_ELECTION
    game.save()

    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    pm.add_title(Senator.Title.ROME_CONSUL)
    pm.add_title(Senator.Title.HRAO)
    pm.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    pm.save()

    Province.objects.create(game=game, name="Sicilia", developed=False)
    return game


@pytest.mark.django_db
def test_end_prosecutions_enters_governor_election_when_forum_province_exists(
    prosecution_setup,
):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup
    Province.objects.create(game=game, name="Sicilia", developed=False)

    # Act
    end_prosecutions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION


@pytest.mark.django_db
def test_skip_prosecution_enters_governor_election_when_forum_province_exists(
    prosecution_setup,
):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup
    Province.objects.create(game=game, name="Sicilia", developed=False)
    faction = _faction_of(julius)

    # Act
    result = CloseProsecutionsAction().execute(
        game.id, faction.id, {}, FakeRandomResolver()
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION


@pytest.mark.parametrize("unaligned", [False, True], ids=["aligned", "unaligned"])
@pytest.mark.django_db
def test_governor_elected_leaves_rome_and_assigns_term(
    governor_election_game: Game, resolver: FakeRandomResolver, unaligned: bool
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    province = Province.objects.get(game=game, name="Sicilia")
    faction = _faction_of(pm)

    if unaligned:
        # Unique display_name — ElectGovernorEffect resolves by name, and
        # early-republic families already exist in basic_game.
        candidate = Senator.objects.create(
            game=game,
            family_name="Testonius",
            code="TST",
            faction=None,
            alive=True,
            location="Rome",
            military=1,
            oratory=2,
            loyalty=3,
            influence=4,
        )
    else:
        candidate = senators[1]

    # String IDs match JSON.stringify from the frontend single-province form.
    _propose_single_governor_motion(
        game, faction, province, candidate, string_ids=True
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    province.refresh_from_db()
    candidate.refresh_from_db()
    assert province.governor_id == candidate.id
    assert province.term == 3
    assert province.elected_this_turn is True
    assert candidate.location == "Sicilia"
    if unaligned:
        assert candidate.faction_id is None
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_get_schema_excludes_defeated_governor_pairing_for_selected_province(
    governor_election_game: Game,
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    defeated_candidate = senators[1]
    alternate_candidate = senators[2]
    sicilia = Province.objects.get(game=game, name="Sicilia")
    macedonia = Province.objects.create(game=game, name="Macedonia", developed=True)
    faction = _faction_of(pm)

    game.defeated_proposals = [
        format_governor_proposal(sicilia.name, defeated_candidate)
    ]
    game.save()

    # Act
    actions = ElectGovernorAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert len(actions) == 1
    sicilia_option_ids = _governor_option_ids(actions[0], sicilia.name)
    macedonia_option_ids = _governor_option_ids(actions[0], macedonia.name)

    assert defeated_candidate.id not in sicilia_option_ids
    assert alternate_candidate.id in sicilia_option_ids
    assert defeated_candidate.id in macedonia_option_ids


@pytest.mark.django_db
def test_major_office_holder_ineligible_for_governor_election(
    governor_election_game: Game,
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    consul_candidate = senators[1]
    consul_candidate.add_title(Senator.Title.ROME_CONSUL)
    consul_candidate.save()
    province = Province.objects.get(game=game, name="Sicilia")
    faction = _faction_of(pm)

    # Act
    result = ElectGovernorAction().execute(
        game.id,
        faction.id,
        {"Province": province.id, "Governor": consul_candidate.id},
        FakeRandomResolver(),
    )

    # Assert
    assert not result.success
    assert "ineligible" in (result.message or "").lower()


@pytest.mark.django_db
def test_elected_governor_does_not_contribute_to_later_faction_vote(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    governor = senators[1]
    province = Province.objects.get(game=game, name="Sicilia")
    faction = _faction_of(pm)

    _propose_single_governor_motion(game, faction, province, governor)
    execute_effects_and_manage_actions(game.id, resolver)

    governor.refresh_from_db()
    assert governor.location == province.name

    game.current_proposal = "Deploy forces"
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()
    for f in Faction.objects.filter(game=game):
        f.remove_status_item(FactionStatusItem.DONE)
        f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
        f.save()
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    in_rome_votes = sum(
        s.votes
        for s in faction.senators.filter(alive=True, location="Rome")
    )

    # Act
    result = VoteYeaAction().execute(game.id, faction.id, {}, FakeRandomResolver())

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.votes_yea == in_rome_votes
    governor.refresh_from_db()
    assert not governor.has_status_item(Senator.StatusItem.VOTED_YEA)


@pytest.mark.django_db
def test_auto_close_governor_elections_advances_when_no_eligible_candidates(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    game.current_proposal = None
    game.save()
    for senator in Senator.objects.filter(game=game, alive=True):
        senator.add_title(Senator.Title.ROME_CONSUL)
        senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    log_texts = list(Log.objects.filter(game=game).values_list("text", flat=True))
    assert any(
        "no further governorship elections possible" in text.lower()
        for text in log_texts
    )


@pytest.mark.django_db
def test_governor_death_mid_senate_reopens_governor_election(
    governor_election_game: Game,
):
    # Arrange
    # Active other-business motion and prior defeats must survive the death.
    game = governor_election_game
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    defeated_concession = "Award the Harbor Fees concession to Cornelius"
    game.current_proposal = "Deploy forces"
    game.votes_yea = 5
    game.votes_nay = 3
    game.defeated_proposals = [defeated_concession]
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    governor = senators[1]
    province = Province.objects.get(game=game, name="Sicilia")
    province.governor = governor
    province.term = 3
    province.elected_this_turn = True
    province.save()
    governor.location = province.name
    governor.save()
    faction = _faction_of(senators[0])
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()

    # Act
    kill_senator(governor)

    # Assert
    province.refresh_from_db()
    game.refresh_from_db()
    faction.refresh_from_db()
    assert province.governor_id is None
    assert province.term is None
    assert province.elected_this_turn is False
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION
    assert game.current_proposal is None or game.current_proposal == ""
    assert game.votes_yea == 0
    assert game.votes_nay == 0
    assert defeated_concession in game.defeated_proposals
    assert not faction.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
    assert not faction.has_status_item(FactionStatusItem.DONE)


@pytest.mark.django_db
def test_candidate_death_before_resolution_logs_and_keeps_governor_election(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    candidate = senators[1]
    province = Province.objects.get(game=game, name="Sicilia")
    faction = _faction_of(pm)
    candidate_name = candidate.display_name

    _propose_single_governor_motion(game, faction, province, candidate)
    kill_senator(candidate)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    province.refresh_from_db()
    game.refresh_from_db()
    assert province.governor_id is None
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION
    log_texts = list(Log.objects.filter(game=game).values_list("text", flat=True))
    assert any(
        f"{candidate_name} could not take up the governorship of {province.name}"
        in text
        for text in log_texts
    )


@pytest.mark.django_db
def test_grouped_governor_election_assigns_multiple_governors(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    sicilia_governor = senators[1]
    macedonia_governor = senators[2]
    sicilia = Province.objects.get(game=game, name="Sicilia")
    macedonia = Province.objects.create(game=game, name="Macedonia", developed=True)
    faction = _faction_of(pm)

    result = ElectGovernorAction().execute(
        game.id,
        faction.id,
        {
            "Provinces": [sicilia.id, macedonia.id],
            governor_field_name(sicilia.name): sicilia_governor.id,
            governor_field_name(macedonia.name): macedonia_governor.id,
        },
        FakeRandomResolver(),
    )
    assert result.success

    game.refresh_from_db()
    expected_proposal = format_grouped_governor_proposal(
        [(sicilia, sicilia_governor), (macedonia, macedonia_governor)]
    )
    assert game.current_proposal == expected_proposal

    game.votes_yea = 15
    game.votes_nay = 0
    game.save()
    _setup_all_factions_done(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    sicilia.refresh_from_db()
    macedonia.refresh_from_db()
    sicilia_governor.refresh_from_db()
    macedonia_governor.refresh_from_db()
    assert sicilia.governor_id == sicilia_governor.id
    assert macedonia.governor_id == macedonia_governor.id
    assert sicilia_governor.location == "Sicilia"
    assert macedonia_governor.location == "Macedonia"
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_grouped_governor_defeat_allows_separate_pairings_in_schema(
    governor_election_game: Game,
):
    # Arrange
    # 1.09.131: joint defeat does not lock individual pairings.
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    sicilia_candidate = senators[1]
    macedonia_candidate = senators[2]
    sicilia = Province.objects.get(game=game, name="Sicilia")
    macedonia = Province.objects.create(game=game, name="Macedonia", developed=True)
    faction = _faction_of(pm)

    joint = format_grouped_governor_proposal(
        [(sicilia, sicilia_candidate), (macedonia, macedonia_candidate)]
    )
    game.defeated_proposals = [joint]
    game.save()

    # Act
    actions = ElectGovernorAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert len(actions) == 1
    assert sicilia_candidate.id in _governor_option_ids(actions[0], sicilia.name)
    assert macedonia_candidate.id in _governor_option_ids(actions[0], macedonia.name)
    sicilia_field = next(
        f
        for f in actions[0].field_descriptors
        if f["name"] == governor_field_name(sicilia.name)
    )
    assert sicilia_field.get("conditions")

    # Exact joint motion may not be reintroduced
    result = ElectGovernorAction().execute(
        game.id,
        faction.id,
        {
            "Provinces": [sicilia.id, macedonia.id],
            governor_field_name(sicilia.name): sicilia_candidate.id,
            governor_field_name(macedonia.name): macedonia_candidate.id,
        },
        FakeRandomResolver(),
    )
    assert not result.success
    assert "rejected" in (result.message or "").lower()


@pytest.mark.django_db
def test_grouped_governor_election_rejects_duplicate_senator(
    governor_election_game: Game,
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    candidate = senators[1]
    sicilia = Province.objects.get(game=game, name="Sicilia")
    macedonia = Province.objects.create(game=game, name="Macedonia", developed=True)
    faction = _faction_of(pm)

    # Act
    result = ElectGovernorAction().execute(
        game.id,
        faction.id,
        {
            "Provinces": [sicilia.id, macedonia.id],
            governor_field_name(sicilia.name): candidate.id,
            governor_field_name(macedonia.name): candidate.id,
        },
        FakeRandomResolver(),
    )

    # Assert
    assert not result.success
    assert "multiple provinces" in (result.message or "").lower()


@pytest.mark.django_db
def test_close_senate_blocked_while_vacant_forum_province_has_eligible_candidates(
    governor_election_game: Game,
):
    # Arrange
    game = governor_election_game
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    pm = Senator.objects.filter(game=game, alive=True).first()
    assert pm is not None and pm.faction_id is not None
    faction = _faction_of(pm)

    # Act
    result = CloseSenateAction().execute(game.id, faction.id, {}, FakeRandomResolver())

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_last_remaining_governor_candidate_is_auto_appointed(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    game.current_proposal = None
    senators = list(Senator.objects.filter(game=game, alive=True))
    province = Province.objects.get(game=game, name="Sicilia")
    last = next(
        s for s in senators if not s.has_title(Senator.Title.ROME_CONSUL)
    )
    defeated = [
        format_governor_proposal(province.name, s)
        for s in senators
        if s.id != last.id and not s.has_title(Senator.Title.ROME_CONSUL)
    ]
    game.defeated_proposals = defeated
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    province.refresh_from_db()
    last.refresh_from_db()
    game.refresh_from_db()
    assert province.governor_id == last.id
    assert province.term == 3
    assert last.location == "Sicilia"
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    log_texts = list(Log.objects.filter(game=game).values_list("text", flat=True))
    assert any("automatically appointed governor of Sicilia" in text for text in log_texts)


@pytest.mark.django_db
def test_sole_eligible_governor_candidate_is_auto_appointed(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    last = next(s for s in senators if not s.has_title(Senator.Title.ROME_CONSUL))
    for senator in senators:
        if senator.id != last.id and not senator.has_title(Senator.Title.ROME_CONSUL):
            senator.location = "captive"
            senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    province = Province.objects.get(game=game, name="Sicilia")
    last.refresh_from_db()
    game.refresh_from_db()
    assert province.governor_id == last.id
    assert last.location == "Sicilia"
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_close_senate_allowed_when_no_eligible_governor_candidates(
    governor_election_game: Game,
):
    # Arrange
    game = governor_election_game
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    for senator in Senator.objects.filter(game=game, alive=True):
        if not senator.has_title(Senator.Title.ROME_CONSUL):
            senator.add_title(Senator.Title.FIELD_CONSUL)
            senator.save()
    pm = Senator.objects.filter(game=game, alive=True).first()
    assert pm is not None
    faction = _faction_of(pm)

    # Act
    result = CloseSenateAction().execute(game.id, faction.id, {}, FakeRandomResolver())

    # Assert
    assert result.success


@pytest.mark.django_db
def test_passing_one_governor_preserves_defeated_pairings_for_other_provinces(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    # 1.09.131: stay in GOVERNOR_ELECTION without wiping defeats.
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    sicilia_candidate = senators[1]
    macedonia_candidate = senators[2]
    sicilia = Province.objects.get(game=game, name="Sicilia")
    macedonia = Province.objects.create(game=game, name="Macedonia", developed=True)
    faction = _faction_of(pm)
    defeated = format_governor_proposal(macedonia.name, macedonia_candidate)
    game.defeated_proposals = [defeated]
    game.save()

    _propose_single_governor_motion(game, faction, sicilia, sicilia_candidate)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    sicilia.refresh_from_db()
    assert sicilia.governor_id == sicilia_candidate.id
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION
    assert defeated in game.defeated_proposals

    actions = ElectGovernorAction().get_schema(GameStateSnapshot(game.id), faction.id)
    assert len(actions) == 1
    # Only Macedonia remains vacant → single-province schema uses "Governor"
    governor_field = next(
        f for f in actions[0].field_descriptors if f["name"] == "Governor"
    )
    governor_ids = {option["id"] for option in governor_field["options"]}
    assert macedonia_candidate.id not in governor_ids


@pytest.mark.django_db
def test_advanced_vote_accepts_rome_only_keys_after_governor_leaves(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    governor = senators[1]
    province = Province.objects.get(game=game, name="Sicilia")
    faction = _faction_of(pm)

    _propose_single_governor_motion(game, faction, province, governor)
    execute_effects_and_manage_actions(game.id, resolver)

    governor.refresh_from_db()
    assert governor.location == province.name

    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = "Deploy forces"
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()
    for f in Faction.objects.filter(game=game):
        f.remove_status_item(FactionStatusItem.DONE)
        f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
        f.save()
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()

    attending = faction_senators_attending_senate(game.id, faction)
    assert all(s.id != governor.id for s in attending)
    senator_votes = {
        str(s.id): {"decision": "yea", "bought_votes": 0} for s in attending
    }
    with_governor_votes = {
        **senator_votes,
        str(governor.id): {"decision": "yea", "bought_votes": 0},
    }

    # Act
    # Keys must match Rome attendees only.
    assert not AdvancedVoteAction().execute(
        game.id,
        faction.id,
        {"senator_votes": with_governor_votes},
        FakeRandomResolver(),
    ).success

    # Assert
    assert AdvancedVoteAction().execute(
        game.id, faction.id, {"senator_votes": senator_votes}, FakeRandomResolver()
    ).success


@pytest.mark.django_db
def test_non_pm_faction_can_play_tribune_and_nominate_governor(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    candidate = senators[1]
    province = Province.objects.get(game=game, name="Sicilia")
    non_pm_faction = next(
        f for f in Faction.objects.filter(game=game) if f.id != pm.faction_id
    )
    non_pm_faction.cards = ["tribune"]
    non_pm_faction.save()

    # Act
    tribune = PlayTribuneAction().execute(
        game.id, non_pm_faction.id, {}, resolver
    )
    snapshot = GameStateSnapshot(game.id)
    elect_allowed = ElectGovernorAction().is_allowed(snapshot, non_pm_faction.id)
    pm_allowed = ElectGovernorAction().is_allowed(snapshot, pm.faction_id)
    result = ElectGovernorAction().execute(
        game.id,
        non_pm_faction.id,
        {"Province": province.id, "Governor": candidate.id},
        resolver,
    )

    # Assert
    assert tribune.success
    assert elect_allowed is not None
    assert pm_allowed is None
    assert result.success
    game.refresh_from_db()
    assert "Elect governor of Sicilia:" in (game.current_proposal or "")


@pytest.mark.django_db
def test_governor_death_during_consular_election_does_not_skip_ahead(
    governor_election_game: Game,
):
    # Arrange
    game = governor_election_game
    game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    governor = senators[1]
    province = Province.objects.get(game=game, name="Sicilia")
    province.governor = governor
    province.term = 3
    province.save()
    governor.location = province.name
    governor.save()

    # Act
    kill_senator(governor)

    # Assert
    game.refresh_from_db()
    province.refresh_from_db()
    assert province.governor_id is None
    assert game.sub_phase == Game.SubPhase.CONSULAR_ELECTION


def _make_sole_eligible_candidate(game: Game) -> Senator:
    senators = list(Senator.objects.filter(game=game, alive=True))
    last = next(s for s in senators if not s.has_title(Senator.Title.ROME_CONSUL))
    for senator in senators:
        if senator.id != last.id and not senator.has_title(Senator.Title.ROME_CONSUL):
            senator.add_title(Senator.Title.FIELD_CONSUL)
            senator.save()
    return last


@pytest.mark.django_db
def test_unaligned_governor_cannot_be_persuaded(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    province = Province.objects.get(game=game, name="Sicilia")
    faction = _faction_of(pm)
    candidate = Senator.objects.create(
        game=game,
        family_name="Testonius",
        code="TST",
        faction=None,
        alive=True,
        location="Rome",
        military=1,
        oratory=2,
        loyalty=3,
        influence=4,
    )
    _propose_single_governor_motion(game, faction, province, candidate)
    execute_effects_and_manage_actions(game.id, resolver)
    candidate.refresh_from_db()
    assert candidate.location == "Sicilia"

    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.PERSUASION_ATTEMPT
    game.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    persuader = next(
        s for s in senators if s.faction_id == faction.id and s.location == "Rome"
    )
    persuader.oratory = 5
    persuader.influence = 5
    persuader.talents = 5
    persuader.save()

    # Act
    result = AttemptPersuasionAction().execute(
        game.id,
        faction.id,
        {
            "Persuader": str(persuader.id),
            "Target": str(candidate.id),
            "Talents": "0",
        },
        resolver,
    )

    # Assert
    assert not result.success
    assert "not in rome" in (result.message or "").lower()


@pytest.mark.django_db
def test_electing_hrao_governor_transfers_presiding_magistrate(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(
        Senator.objects.filter(game=game, alive=True, faction__isnull=False)
    )
    pm = senators[0]
    pm.remove_title(Senator.Title.ROME_CONSUL)
    pm.influence = 5
    pm.save()
    successor = senators[2]
    for senator in senators[1:]:
        senator.influence = 1
        senator.save()
    successor.influence = 20
    successor.save()
    province = Province.objects.get(game=game, name="Sicilia")
    faction = _faction_of(pm)
    _propose_single_governor_motion(game, faction, province, pm)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    pm.refresh_from_db()
    successor.refresh_from_db()
    province.refresh_from_db()
    assert province.governor_id == pm.id
    assert pm.location == "Sicilia"
    assert not pm.has_title(Senator.Title.HRAO)
    assert not pm.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    assert successor.has_title(Senator.Title.HRAO)
    assert successor.has_title(Senator.Title.PRESIDING_MAGISTRATE)


@pytest.mark.django_db
def test_sole_candidate_with_two_vacancies_is_not_auto_appointed(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    last = _make_sole_eligible_candidate(game)
    Province.objects.create(game=game, name="Macedonia", developed=True)
    pm = Senator.objects.filter(game=game, alive=True).first()
    assert pm is not None
    faction = _faction_of(pm)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    last.refresh_from_db()
    game.refresh_from_db()
    sicilia = Province.objects.get(game=game, name="Sicilia")
    macedonia = Province.objects.get(game=game, name="Macedonia")
    assert last.location == "Rome"
    assert sicilia.governor_id is None
    assert macedonia.governor_id is None
    assert game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION
    actions = ElectGovernorAction().get_schema(GameStateSnapshot(game.id), faction.id)
    assert len(actions) == 1
    assert any(field["name"] == "Provinces" for field in actions[0].field_descriptors)


@pytest.mark.django_db
def test_sole_candidate_may_be_elected_to_one_of_two_vacancies(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    last = _make_sole_eligible_candidate(game)
    sicilia = Province.objects.get(game=game, name="Sicilia")
    macedonia = Province.objects.create(game=game, name="Macedonia", developed=True)
    pm = Senator.objects.filter(game=game, alive=True).first()
    assert pm is not None
    faction = _faction_of(pm)

    result = ElectGovernorAction().execute(
        game.id,
        faction.id,
        {
            "Provinces": [sicilia.id],
            governor_field_name(sicilia.name): last.id,
        },
        FakeRandomResolver(),
    )
    assert result.success
    game.refresh_from_db()
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()
    _setup_all_factions_done(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    sicilia.refresh_from_db()
    macedonia.refresh_from_db()
    last.refresh_from_db()
    game.refresh_from_db()
    assert sicilia.governor_id == last.id
    assert last.location == "Sicilia"
    assert macedonia.governor_id is None
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_newly_elected_governor_cannot_be_assassinated(
    governor_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = governor_election_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm = senators[0]
    governor = senators[1]
    province = Province.objects.get(game=game, name="Sicilia")
    faction = _faction_of(pm)
    _propose_single_governor_motion(game, faction, province, governor)
    execute_effects_and_manage_actions(game.id, resolver)
    governor.refresh_from_db()
    assert governor.location == province.name

    assassin_faction = next(
        f for f in Faction.objects.filter(game=game) if f.id != faction.id
    )
    assassin = Senator.objects.filter(
        game=game, faction=assassin_faction, alive=True, location="Rome"
    ).first()
    assert assassin is not None

    # Act
    schema = AttemptAssassinationAction().get_schema(
        GameStateSnapshot(game.id), assassin_faction.id
    )
    result = AttemptAssassinationAction().execute(
        game.id,
        assassin_faction.id,
        {"Assassin": assassin.id, "Target": governor.id},
        FakeRandomResolver(),
    )

    # Assert
    assert not result.success
    assert "not available" in (result.message or "").lower()
    target_ids = set()
    for action in schema:
        for field in action.field_descriptors:
            if field["name"] == "Target":
                target_ids.update(option["id"] for option in field["options"])
    assert governor.id not in target_ids
