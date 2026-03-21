import pytest
from rorapp.actions.redistribute_talents import RedistributeTalentsAction
from rorapp.actions.transfer_talents import TransferTalentsAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


def _setup_redistribution(game: Game) -> Faction:
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.REDISTRIBUTION
    game.save()

    faction = Faction.objects.get(game=game, position=1)
    faction.treasury = 3
    faction.save()

    senators = list(Senator.objects.filter(game=game, faction=faction))
    senators[0].talents = 5
    senators[0].save()
    senators[1].talents = 2
    senators[1].save()

    return faction


@pytest.mark.django_db
def test_redistribute_talents_rebalances_senators_and_treasury(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    faction = _setup_redistribution(basic_game)
    senators = list(
        Senator.objects.filter(game=basic_game, faction=faction).order_by("id")
    )
    allocation = {
        f"senator:{senators[0].id}": 1,
        f"senator:{senators[1].id}": 4,
        "faction_treasury": 5,
    }

    # Act
    result = RedistributeTalentsAction().execute(
        basic_game.id, faction.id, {"Allocation": allocation}, resolver
    )

    # Assert
    assert result.success
    senators[0].refresh_from_db()
    senators[1].refresh_from_db()
    faction.refresh_from_db()
    assert senators[0].talents == 1
    assert senators[1].talents == 4
    assert faction.treasury == 5


@pytest.mark.django_db
def test_redistribute_talents_rejected_when_total_does_not_match(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    faction = _setup_redistribution(basic_game)
    senators = list(
        Senator.objects.filter(game=basic_game, faction=faction).order_by("id")
    )
    allocation = {
        f"senator:{senators[0].id}": 5,
        f"senator:{senators[1].id}": 2,
        "faction_treasury": 99,  # total too high
    }

    # Act
    result = RedistributeTalentsAction().execute(
        basic_game.id, faction.id, {"Allocation": allocation}, resolver
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_redistribute_talents_rejected_when_value_is_negative(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    faction = _setup_redistribution(basic_game)
    senators = list(
        Senator.objects.filter(game=basic_game, faction=faction).order_by("id")
    )
    allocation = {
        f"senator:{senators[0].id}": -1,
        f"senator:{senators[1].id}": 8,
        "faction_treasury": 3,
    }

    # Act
    result = RedistributeTalentsAction().execute(
        basic_game.id, faction.id, {"Allocation": allocation}, resolver
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_transfer_talents_cross_faction_succeeds(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    faction = _setup_redistribution(basic_game)
    own_senator = Senator.objects.filter(game=basic_game, faction=faction).first()
    assert own_senator is not None

    other_faction = Faction.objects.get(game=basic_game, position=2)
    other_senator = Senator.objects.filter(
        game=basic_game, faction=other_faction
    ).first()
    assert other_senator is not None

    # Act
    result = TransferTalentsAction().execute(
        basic_game.id,
        faction.id,
        {
            "Sender": f"senator:{own_senator.id}",
            "Recipient": f"senator:{other_senator.id}",
            "Talents": 3,
        },
        resolver,
    )

    # Assert
    assert result.success
    own_senator.refresh_from_db()
    other_senator.refresh_from_db()
    assert own_senator.talents == 2  # was 5, sent 3
    assert other_senator.talents == 3


@pytest.mark.django_db
def test_transfer_talents_to_own_senator_rejected(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    faction = _setup_redistribution(basic_game)
    senators = list(
        Senator.objects.filter(game=basic_game, faction=faction).order_by("id")
    )
    snapshot = GameStateSnapshot(basic_game.id)

    # Act
    result = TransferTalentsAction().execute(
        basic_game.id,
        faction.id,
        {
            "Sender": f"senator:{senators[0].id}",
            "Recipient": f"senator:{senators[1].id}",
            "Talents": 1,
        },
        resolver,
    )

    # Assert
    assert not result.success

    schemas = TransferTalentsAction().get_schema(snapshot, faction.id)
    assert len(schemas) == 1
    recipient_field = next(f for f in schemas[0].schema if f["name"] == "Recipient")
    recipient_ids = [opt["id"] for opt in recipient_field["options"] if "id" in opt]
    own_senator_ids = [s.id for s in senators]
    assert not any(rid in own_senator_ids for rid in recipient_ids)
