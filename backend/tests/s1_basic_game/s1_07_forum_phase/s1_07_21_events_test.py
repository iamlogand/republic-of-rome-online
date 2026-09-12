import pytest
from rorapp.actions.propose_reinforcing_proconsul import (
    ProposeReinforcingProconsulAction,
)
from rorapp.actions.resolve_storm_at_sea import ResolveStormAtSeaAction
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.effects.senate_phase_end import SenatePhaseEndEffect
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.handle_event import handle_storm_at_sea
from rorapp.models import (
    AvailableAction,
    Campaign,
    Faction,
    Fleet,
    Game,
    Legion,
    Log,
    Senator,
    War,
)


def _setup_initiative_roll(game: Game, faction: Faction) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
    game.deck = ["senator:18"]
    game.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()


def _create_war(
    game: Game,
    name: str,
    fleet_support: int,
    naval_strength: int = 0,
) -> War:
    return War.objects.create(
        game=game,
        name=name,
        index=1,
        land_strength=5,
        fleet_support=fleet_support,
        naval_strength=naval_strength,
        spoils=10,
        location="Italy",
        status=War.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_allied_enthusiasm(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_effect(GameEffect.ALLIED_ENTHUSIASM)
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 1


@pytest.mark.django_db
def test_rolling_7_does_not_draw_a_card(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert len(game.deck) == 1


@pytest.mark.django_db
def test_drawing_allied_enthusiasm_twice_escalates_to_extreme(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 2


@pytest.mark.django_db
def test_rolling_unimplemented_event_draws_a_card_instead(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [
        7,
        5,
    ]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert len(game.deck) == 0


@pytest.mark.django_db
def test_storm_at_sea_pauses_for_the_hrao_and_preserves_the_initiative(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    current_faction: Faction = game.factions.get(position=3)
    _setup_initiative_roll(game, current_faction)
    set_hrao(game.id)
    hrao = game.senators.get(titles__contains=[Senator.Title.HRAO.value])
    hrao_faction = hrao.faction
    assert hrao_faction is not None

    war = _create_war(game, "1st Punic War", fleet_support=2)
    commander = game.senators.exclude(faction=hrao_faction).first()
    assert commander is not None
    campaign = Campaign.objects.create(game=game, war=war, commander=commander)
    uncommanded_war = _create_war(game, "1st Macedonian War", fleet_support=0)
    uncommanded_campaign = Campaign.objects.create(
        game=game, war=uncommanded_war, commander=None
    )
    Fleet.objects.create(game=game, number=4, campaign=campaign)
    Fleet.objects.create(game=game, number=2)
    Fleet.objects.create(game=game, number=1)
    Fleet.objects.create(game=game, number=3, campaign=campaign)
    Fleet.objects.create(game=game, number=5)
    Fleet.objects.create(game=game, number=6, campaign=uncommanded_campaign)
    resolver.dice_rolls = [7, 11, 3]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    current_faction.refresh_from_db()
    hrao_faction.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.STORM_AT_SEA
    assert game.storm_at_sea_fleet_losses == 3
    assert current_faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    assert hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert not game.factions.exclude(id=hrao_faction.id).filter(
        status_items__contains=[FactionStatusItem.AWAITING_DECISION.value]
    ).exists()

    actions = AvailableAction.objects.filter(
        game=game, base_name=ResolveStormAtSeaAction.NAME
    )
    assert actions.count() == 1
    action = actions.get(faction=hrao_faction)
    field = action.field_descriptors[0]
    assert field["required_count"] == 3
    assert [option["name"] for option in field["options"]] == [
        "Fleet I",
        "Fleet II",
        "Fleet V",
        "Fleet III",
        "Fleet IV",
        "Fleet VI",
    ]
    assert [option["group"] for option in field["options"][:3]] == [
        "Reserve",
        "Reserve",
        "Reserve",
    ]
    assert field["options"][-1]["group"] == (
        "Uncommanded campaign — 1st Macedonian War"
    )


@pytest.mark.django_db
def test_storm_at_sea_applies_evil_omens_to_its_fleet_loss_roll(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = game.factions.get(position=1)
    game.add_effect(GameEffect.EVIL_OMENS)
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    set_hrao(game.id)
    for number in range(1, 7):
        Fleet.objects.create(game=game, number=number)
    resolver.dice_rolls = [5]

    # Act
    advances = handle_storm_at_sea(game, faction, resolver)

    # Assert
    game.refresh_from_db()
    assert not advances
    assert game.storm_at_sea_fleet_losses == 3
    assert game.logs.filter(
        text=(
            f"{faction.display_name} drew storm at sea. "
            "The HRAO must choose 3 Roman fleets to eliminate."
        )
    ).exists()


@pytest.mark.django_db
def test_storm_at_sea_automatically_destroys_all_existing_fleets(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = game.factions.get(position=1)
    game.storm_at_sea_fleet_losses = 4
    game.save()
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()
    Fleet.objects.create(game=game, number=1)
    resolver.dice_rolls = [8]

    # Act
    advances = handle_storm_at_sea(game, faction, resolver)

    # Assert
    assert advances
    game.refresh_from_db()
    faction.refresh_from_db()
    assert game.storm_at_sea_fleet_losses == 0
    assert not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert not Fleet.objects.filter(game=game).exists()
    assert game.logs.filter(text="Storm at sea destroyed 1 fleet (I).").exists()
    assert game.logs.filter(
        text__contains="The only existing Roman fleet must be eliminated."
    ).exists()
    assert not AvailableAction.objects.filter(
        game=game, base_name=ResolveStormAtSeaAction.NAME
    ).exists()


@pytest.mark.django_db
def test_storm_at_sea_has_no_effect_when_rome_has_no_fleets(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = game.factions.get(position=1)
    game.storm_at_sea_fleet_losses = 4
    game.save()
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()
    resolver.dice_rolls = [7]

    # Act
    advances = handle_storm_at_sea(game, faction, resolver)

    # Assert
    assert advances
    game.refresh_from_db()
    faction.refresh_from_db()
    assert game.storm_at_sea_fleet_losses == 0
    assert not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert game.logs.filter(
        text=(
            f"{faction.display_name} drew storm at sea. "
            "Rome had no fleets to lose."
        )
    ).exists()


@pytest.mark.django_db
def test_storm_at_sea_clears_pending_state_when_no_fleets_are_lost(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = game.factions.get(position=1)
    game.storm_at_sea_fleet_losses = 4
    game.add_effect(GameEffect.EVIL_OMENS)
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()
    Fleet.objects.create(game=game, number=1)
    resolver.dice_rolls = [2]

    # Act
    advances = handle_storm_at_sea(game, faction, resolver)

    # Assert
    assert advances
    game.refresh_from_db()
    faction.refresh_from_db()
    assert game.storm_at_sea_fleet_losses == 0
    assert not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert Fleet.objects.filter(game=game, number=1).exists()
    assert game.logs.filter(
        text=f"{faction.display_name} drew storm at sea. No fleets were lost."
    ).exists()


@pytest.mark.django_db
def test_hrao_selects_exact_fleets_and_new_support_failures_are_logged(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    current_faction = game.factions.get(position=3)
    _setup_initiative_roll(game, current_faction)
    set_hrao(game.id)
    hrao = game.senators.get(titles__contains=[Senator.Title.HRAO.value])
    hrao_faction = hrao.faction
    assert hrao_faction is not None

    commanders = list(game.senators.exclude(faction=hrao_faction)[:2])
    assert len(commanders) == 2
    land_war = _create_war(game, "1st Punic War", fleet_support=1)
    naval_war = _create_war(game, "1st Illyrian War", fleet_support=0, naval_strength=4)
    land_campaign = Campaign.objects.create(
        game=game, war=land_war, commander=commanders[0]
    )
    naval_campaign = Campaign.objects.create(
        game=game, war=naval_war, commander=commanders[1]
    )
    land_fleet = Fleet.objects.create(game=game, number=1, campaign=land_campaign)
    naval_fleet = Fleet.objects.create(game=game, number=2, campaign=naval_campaign)
    Legion.objects.create(game=game, number=1, campaign=land_campaign)
    Fleet.objects.create(game=game, number=3)
    resolver.dice_rolls = [7, 11, 2]
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [land_fleet.id, naval_fleet.id]},
        resolver,
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    hrao_faction.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.PERSUASION_ATTEMPT
    assert game.storm_at_sea_fleet_losses == 0
    assert not hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert not Fleet.objects.filter(id__in=[land_fleet.id, naval_fleet.id]).exists()
    assert Fleet.objects.filter(game=game, number=3, campaign__isnull=True).exists()
    assert game.logs.filter(
        text__contains="no longer has sufficient fleet support for its land battle"
    ).exists()
    assert game.logs.filter(
        text__contains="no longer has any fleets for its naval battle"
    ).exists()


@pytest.mark.django_db
def test_storm_at_sea_rejects_an_invalid_or_stale_fleet_selection(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = game.factions.get(position=1)
    game.phase = Game.Phase.FORUM
    game.save()
    set_hrao(game.id)
    hrao = game.senators.get(titles__contains=[Senator.Title.HRAO.value])
    hrao_faction = hrao.faction
    assert hrao_faction is not None
    for number in range(1, 4):
        Fleet.objects.create(game=game, number=number)
    resolver.dice_rolls = [2]
    advances = handle_storm_at_sea(game, faction, resolver)
    assert not advances
    fleets = list(Fleet.objects.filter(game=game).order_by("number"))

    # Act and assert
    too_few_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id]},
        resolver,
    )
    assert not too_few_result.success
    assert too_few_result.message == "Select exactly 2 Roman fleets."

    too_many_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {
            ResolveStormAtSeaAction.FLEETS_FIELD: [
                fleets[0].id,
                fleets[1].id,
                fleets[2].id,
            ]
        },
        resolver,
    )
    assert not too_many_result.success
    assert too_many_result.message == "Select exactly 2 Roman fleets."

    other_faction = game.factions.exclude(id=hrao_faction.id).first()
    assert other_faction is not None
    non_hrao_result = ResolveStormAtSeaAction().execute(
        game.id,
        other_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id, fleets[1].id]},
        resolver,
    )
    assert not non_hrao_result.success
    assert non_hrao_result.message == "No storm at sea decision is pending."

    other_game = Game.objects.create(name="Other game", host=game.host)
    other_game_fleet = Fleet.objects.create(game=other_game, number=1)
    wrong_game_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {
            ResolveStormAtSeaAction.FLEETS_FIELD: [
                fleets[0].id,
                other_game_fleet.id,
            ]
        },
        resolver,
    )
    assert not wrong_game_result.success
    assert wrong_game_result.message == (
        "One or more selected fleets no longer exist."
    )

    duplicate_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id, fleets[0].id]},
        resolver,
    )
    assert not duplicate_result.success
    assert duplicate_result.message == "Select exactly 2 Roman fleets."

    hrao.location = "Sicilia"
    hrao.save()
    offsite_hrao_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id, fleets[1].id]},
        resolver,
    )
    assert not offsite_hrao_result.success
    assert offsite_hrao_result.message == (
        "Only the HRAO faction may resolve this event."
    )
    hrao.location = "Rome"
    hrao.save()

    stale_fleet_id = fleets[1].id
    fleets[1].delete()
    stale_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id, stale_fleet_id]},
        resolver,
    )
    assert not stale_result.success
    assert stale_result.message == "One or more selected fleets no longer exist."

    invalid_type_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id, 2.5]},
        resolver,
    )
    assert not invalid_type_result.success
    assert invalid_type_result.message == "Invalid Roman fleet selection."

    success_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id, fleets[2].id]},
        resolver,
    )
    assert success_result.success

    repeated_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id, fleets[2].id]},
        resolver,
    )
    assert not repeated_result.success
    assert repeated_result.message == "No storm at sea decision is pending."


@pytest.mark.django_db
def test_additional_storms_at_sea_are_resolved_normally(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = game.factions.get(position=1)
    game.phase = Game.Phase.FORUM
    game.save()
    set_hrao(game.id)
    hrao = game.senators.get(titles__contains=[Senator.Title.HRAO.value])
    hrao_faction = hrao.faction
    assert hrao_faction is not None
    fleets = [
        Fleet.objects.create(game=game, number=number) for number in range(1, 6)
    ]

    # Act
    resolver.dice_rolls = [2]
    assert not handle_storm_at_sea(game, faction, resolver)
    first_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[0].id, fleets[1].id]},
        resolver,
    )

    resolver.dice_rolls = [2]
    assert not handle_storm_at_sea(game, faction, resolver)
    second_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [fleets[2].id, fleets[3].id]},
        resolver,
    )

    # Assert
    assert first_result.success
    assert second_result.success
    assert list(Fleet.objects.filter(game=game).values_list("number", flat=True)) == [
        5
    ]
    assert game.logs.filter(text__startswith="Storm at sea destroyed").count() == 2


@pytest.mark.django_db
def test_campaign_without_restored_fleet_support_is_recalled_at_senate_end(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = game.factions.get(position=1)
    game.phase = Game.Phase.FORUM
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    set_hrao(game.id)
    hrao = game.senators.get(titles__contains=[Senator.Title.HRAO.value])
    hrao_faction = hrao.faction
    assert hrao_faction is not None

    commander = game.senators.exclude(faction=hrao_faction).first()
    assert commander is not None
    commander.location = "Sicilia"
    commander.save()
    war = _create_war(game, "1st Punic War", fleet_support=1)
    campaign = Campaign.objects.create(game=game, war=war, commander=commander)
    legion = Legion.objects.create(game=game, number=1, campaign=campaign)
    deployed_fleet = Fleet.objects.create(game=game, number=1, campaign=campaign)
    Fleet.objects.create(game=game, number=2)

    resolver.dice_rolls = [2]
    assert not handle_storm_at_sea(game, faction, resolver)
    storm_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [deployed_fleet.id]},
        resolver,
    )
    assert storm_result.success

    # Act
    game.refresh_from_db()
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.END
    game.save()
    SenatePhaseEndEffect().execute(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    legion.refresh_from_db()
    assert not Campaign.objects.filter(id=campaign.id).exists()
    assert commander.location == "Rome"
    assert legion.campaign_id is None
    assert Fleet.objects.filter(game=game, number=2, campaign__isnull=True).exists()


@pytest.mark.django_db
def test_campaign_with_restored_fleet_support_is_not_recalled_at_senate_end(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction = game.factions.get(position=1)
    game.phase = Game.Phase.FORUM
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    set_hrao(game.id)
    hrao = game.senators.get(titles__contains=[Senator.Title.HRAO.value])
    hrao_faction = hrao.faction
    assert hrao_faction is not None
    hrao.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    hrao.save()

    commander = game.senators.exclude(faction=hrao_faction).first()
    assert commander is not None
    commander.location = "Sicilia"
    commander.save()
    war = _create_war(game, "1st Punic War", fleet_support=1)
    campaign = Campaign.objects.create(
        game=game,
        war=war,
        commander=commander,
        recently_deployed=False,
    )
    Legion.objects.create(game=game, number=1, campaign=campaign)
    deployed_fleet = Fleet.objects.create(game=game, number=1, campaign=campaign)
    reserve_fleet = Fleet.objects.create(
        game=game,
        number=2,
        recently_raised=False,
    )

    resolver.dice_rolls = [2]
    assert not handle_storm_at_sea(game, faction, resolver)
    storm_result = ResolveStormAtSeaAction().execute(
        game.id,
        hrao_faction.id,
        {ResolveStormAtSeaAction.FLEETS_FIELD: [deployed_fleet.id]},
        resolver,
    )
    assert storm_result.success

    game.refresh_from_db()
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    proposal_result = ProposeReinforcingProconsulAction().execute(
        game.id,
        hrao_faction.id,
        {
            "Campaign": campaign.id,
            "Fleets": [reserve_fleet.id],
        },
        resolver,
    )
    assert proposal_result.success

    game.refresh_from_db()
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()
    factions = list(game.factions.all())
    for voting_faction in factions:
        voting_faction.add_status_item(FactionStatusItem.DONE)
    Faction.objects.bulk_update(factions, ["status_items"])
    execute_effects_and_manage_actions(game.id, resolver)

    reserve_fleet.refresh_from_db()
    assert reserve_fleet.campaign_id == campaign.id

    # Act
    game.refresh_from_db()
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.END
    game.save()
    SenatePhaseEndEffect().execute(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    reserve_fleet.refresh_from_db()
    assert Campaign.objects.filter(id=campaign.id).exists()
    assert commander.location == "Sicilia"
    assert reserve_fleet.campaign_id == campaign.id
    assert not game.logs.filter(
        text__contains=(
            "automatically recalled from the 1st Punic War due to "
            "insufficient fleet support"
        )
    ).exists()


@pytest.mark.django_db
def test_rolling_7_with_evil_omens_event_roll_adds_effect(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_effect(GameEffect.EVIL_OMENS)
    assert game.count_effect(GameEffect.EVIL_OMENS) == 1


@pytest.mark.django_db
def test_evil_omens_costs_20T_on_first_draw(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 80


@pytest.mark.django_db
def test_evil_omens_second_draw_does_not_cost_additional_20T(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 100



@pytest.mark.django_db
def test_evil_omens_does_not_affect_initiative_roll(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_effect(GameEffect.ALLIED_ENTHUSIASM)


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_drought(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 9]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.DROUGHT) == 1


@pytest.mark.django_db
def test_drawing_drought_beyond_severe_still_increases_famine(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.DROUGHT)
    game.add_effect(GameEffect.DROUGHT)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 9]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.DROUGHT) == 3


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_manpower_shortage(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 12]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.MANPOWER_SHORTAGE) == 1


@pytest.mark.django_db
def test_drawing_manpower_shortage_twice_stacks(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.MANPOWER_SHORTAGE)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 12]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.MANPOWER_SHORTAGE) == 2


@pytest.mark.django_db
def test_drawing_allied_enthusiasm_at_max_has_no_effect(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 2


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_epidemic(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["1"]]
    victim = game.senators.get(code="1")

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    victim.refresh_from_db()
    assert victim.alive == False


@pytest.mark.django_db
def test_epidemic_kills_every_senator_in_rome_that_is_drawn(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["1", "5"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert game.senators.filter(code="1", alive=True).count() == 0
    assert game.senators.filter(code="5", alive=True).count() == 0


@pytest.mark.django_db
def test_epidemic_does_not_kill_senators_away_from_rome(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    commander = game.senators.get(code="1")
    commander.location = "Sicilia"
    commander.save()
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["1"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.alive == True




@pytest.mark.django_db
def test_epidemic_without_matching_chits_kills_nobody(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["21", "22", "23", "24", "25", "26"]]
    senator_count = game.senators.filter(alive=True).count()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert game.senators.filter(alive=True).count() == senator_count


@pytest.mark.django_db
def test_epidemic_killing_the_hrao_and_his_successor_leaves_a_new_hrao(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    set_hrao(game.id)
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["1", "2"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert (
        game.senators.filter(
            alive=True, titles__contains=[Senator.Title.HRAO.value]
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_epidemic_does_not_promote_a_senator_who_dies_in_it(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    set_hrao(game.id)
    resolver.dice_rolls = [7, 8]
    resolver.mortality_chits = [["1", "2"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert not game.logs.filter(text__startswith="Fabius").filter(
        text__endswith="became HRAO."
    ).exists()


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_natural_disaster(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.NATURAL_DISASTER) == 1


@pytest.mark.django_db
def test_natural_disaster_costs_50T_on_first_draw(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 50


@pytest.mark.django_db
def test_natural_disaster_second_draw_does_not_cost_additional_50T(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.add_effect(GameEffect.NATURAL_DISASTER)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 100


@pytest.mark.django_db
def test_natural_disaster_second_draw_still_destroys_a_concession(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.NATURAL_DISASTER)
    game.add_concession(Concession.MINING)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.NATURAL_DISASTER) == 2
    assert game.has_destroyed_concession(Concession.MINING)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "concession_roll, concession",
    [
        (1, Concession.MINING),
        (2, Concession.MINING),
        (3, Concession.HARBOR_FEES),
        (4, Concession.HARBOR_FEES),
        (5, Concession.ARMAMENTS),
        (6, Concession.SHIP_BUILDING),
    ],
)
def test_natural_disaster_destroys_the_rolled_concession(
    basic_game: Game,
    resolver: FakeRandomResolver,
    concession_roll: int,
    concession: Concession,
):
    # Arrange
    game = basic_game
    for value in Concession:
        game.add_concession(value)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, concession_roll]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.destroyed_concessions == [concession.value]
    assert not game.has_concession(concession)


@pytest.mark.django_db
def test_natural_disaster_takes_the_concession_from_its_holder(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    holder = game.senators.get(code="1")
    holder.add_concession(Concession.MINING)
    holder.add_corrupt_concession(Concession.MINING)
    holder.save()
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    holder.refresh_from_db()
    assert not holder.has_concession(Concession.MINING)
    assert not holder.has_corrupt_concession(Concession.MINING)
    assert game.has_destroyed_concession(Concession.MINING)
    assert not game.has_concession(Concession.MINING)


@pytest.mark.django_db
def test_natural_disaster_has_no_effect_on_a_concession_out_of_play(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    faction.add_card(f"concession:{Concession.MINING.value}")
    faction.save()
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    faction.refresh_from_db()
    assert game.destroyed_concessions == []
    assert faction.has_card(f"concession:{Concession.MINING.value}")
    assert not Log.objects.filter(game=game, text__contains="mining").exists()


@pytest.mark.django_db
def test_natural_disaster_has_no_effect_on_an_already_destroyed_concession(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_destroyed_concession(Concession.MINING)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.destroyed_concessions == [Concession.MINING.value]
    assert not game.has_concession(Concession.MINING)


@pytest.mark.django_db
def test_evil_omens_do_not_modify_the_natural_disaster_roll(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.add_concession(Concession.MINING)
    game.add_concession(Concession.HARBOR_FEES)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 3]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_destroyed_concession(Concession.HARBOR_FEES)
    assert not game.has_destroyed_concession(Concession.MINING)


@pytest.mark.django_db
def test_widespread_natural_disaster_destroys_more_without_further_payment(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.state_treasury = 100
    game.add_concession(Concession.MINING)
    game.add_concession(Concession.ARMAMENTS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 1]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)
    game.refresh_from_db()
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 4, 5]
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.NATURAL_DISASTER) == 2
    assert game.state_treasury == 50
    assert game.has_destroyed_concession(Concession.MINING)
    assert game.has_destroyed_concession(Concession.ARMAMENTS)
