from typing import List, Optional

import pytest
from rorapp.actions.attract_knight import AttractKnightAction
from rorapp.actions.initiative_auction_bid import InitiativeAuctionBidAction
from rorapp.actions.nominate_consuls import NominateConsulsAction
from rorapp.actions.propose_awarding_concession import ProposeAwardingConcessionAction
from rorapp.actions.propose_minor_prosecution import ProposeMinorProsecutionAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator


def _option_ids(
    available_actions: List[AvailableAction], field_name: str
) -> List[int]:
    ids: List[int] = []
    for available_action in available_actions:
        for field in available_action.field_descriptors:
            if field["name"] == field_name:
                ids.extend(option["id"] for option in field["options"])
    return ids


def _send_abroad(senator: Optional[Senator]) -> Senator:
    assert senator is not None
    senator.location = "Sicilia"
    senator.save()
    return senator


@pytest.mark.django_db
def test_senator_away_from_rome_is_not_a_consul_candidate(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
    game.save()
    faction: Faction = game.factions.get(position=1)
    presiding = faction.senators.filter(alive=True).first()
    assert presiding is not None
    presiding.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    presiding.save()
    abroad = _send_abroad(game.factions.get(position=2).senators.first())

    # Act
    schema = NominateConsulsAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert presiding.id in _option_ids(schema, "Consul 1")
    assert abroad.id not in _option_ids(schema, "Consul 1")
    assert abroad.id not in _option_ids(schema, "Consul 2")


@pytest.mark.django_db
def test_senator_away_from_rome_may_not_be_elected_consul(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
    game.save()
    faction: Faction = game.factions.get(position=1)
    senators = list(Senator.objects.filter(game=game, alive=True))
    abroad = _send_abroad(senators[0])

    # Act
    result = NominateConsulsAction().execute(
        game.id,
        faction.id,
        {"Consul 1": abroad.id, "Consul 2": senators[1].id},
        resolver,
    )

    # Assert
    assert not result.success
    game.refresh_from_db()
    assert not game.current_proposal


@pytest.mark.django_db
def test_senator_away_from_rome_may_not_bid_for_an_initiative(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_AUCTION
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_BIDDER)
    faction.save()
    for senator in faction.senators.all():
        senator.talents = 0
        senator.save()
    solvent = faction.senators.first()
    assert solvent is not None
    solvent.talents = 10
    solvent.save()

    # Act
    snapshot = GameStateSnapshot(game.id)
    allowed_from_rome = InitiativeAuctionBidAction().is_allowed(snapshot, faction.id)
    _send_abroad(solvent)
    allowed_from_abroad = InitiativeAuctionBidAction().is_allowed(
        GameStateSnapshot(game.id), faction.id
    )

    # Assert
    assert allowed_from_rome is not None
    assert allowed_from_abroad is None


@pytest.mark.django_db
def test_senator_away_from_rome_is_not_offered_a_knight(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    abroad = _send_abroad(faction.senators.first())

    # Act
    schema = AttractKnightAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert abroad.id not in _option_ids(schema, "Senator")


@pytest.mark.django_db
def test_senator_away_from_rome_may_not_be_awarded_a_concession(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    faction: Faction = game.factions.get(position=1)
    presiding = faction.senators.filter(alive=True).first()
    assert presiding is not None
    presiding.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    presiding.save()
    abroad = _send_abroad(game.factions.get(position=2).senators.first())

    # Act
    schema = ProposeAwardingConcessionAction().get_schema(
        GameStateSnapshot(game.id), faction.id
    )

    # Assert
    assert abroad.id not in _option_ids(schema, "Senator")


@pytest.mark.django_db
def test_senator_away_from_rome_may_not_be_prosecuted(prosecution_setup):
    # Arrange
    game, censor, corrupt, _ = prosecution_setup
    faction = censor.faction
    assert faction is not None
    corrupt.add_status_item(Senator.StatusItem.MAJOR_CORRUPT)
    corrupt.save()

    # Act
    action = ProposeMinorProsecutionAction()
    accused_in_rome = _option_ids(
        action.get_schema(GameStateSnapshot(game.id), faction.id), "Accused"
    )
    _send_abroad(corrupt)
    accused_abroad = _option_ids(
        action.get_schema(GameStateSnapshot(game.id), faction.id), "Accused"
    )

    # Assert
    assert corrupt.id in accused_in_rome
    assert corrupt.id not in accused_abroad
