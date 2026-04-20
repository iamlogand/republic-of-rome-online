import pytest
from rorapp.actions.accept_land_bill_sponsorship import AcceptLandBillSponsorshipAction
from rorapp.actions.propose_passing_land_bill import ProposePassingLandBillAction
from rorapp.actions.refuse_land_bill_sponsorship import RefuseLandBillSponsorshipAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, Senator


def _senators_from_different_factions(game: Game) -> tuple:
    """Return two senators in Rome from different factions."""
    senators = list(
        Senator.objects.filter(game=game, alive=True, location="Rome")
        .exclude(faction__isnull=True)
        .select_related("faction")
    )
    seen_factions = {}
    for senator in senators:
        assert senator.faction
        fid = senator.faction.id
        if fid not in seen_factions:
            seen_factions[fid] = senator
            if len(seen_factions) == 2:
                pair = list(seen_factions.values())
                return pair[0], pair[1]
    raise ValueError("Could not find two senators from different factions in Rome")


def _propose_land_bill(game: Game, resolver: FakeRandomResolver) -> tuple:
    sponsor, cosponsor = _senators_from_different_factions(game)
    faction = sponsor.faction
    ProposePassingLandBillAction().execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Bill type": "II",
            "Sponsor": sponsor.id,
            "Co-sponsor": cosponsor.id,
        },
        random_resolver=resolver,
    )
    sponsor.refresh_from_db()
    cosponsor.refresh_from_db()
    return sponsor, cosponsor


@pytest.mark.django_db
def test_propose_land_bill_sets_consent_required_on_both(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Act
    sponsor, cosponsor = _propose_land_bill(senate_game, resolver)

    # Assert
    assert sponsor.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
    assert cosponsor.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)


@pytest.mark.django_db
def test_propose_land_bill_sets_proposal_string(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Act
    _propose_land_bill(senate_game, resolver)

    # Assert
    senate_game.refresh_from_db()
    assert senate_game.current_proposal is not None
    assert senate_game.current_proposal.startswith("Pass type II land bill")


@pytest.mark.django_db
def test_partial_consent_preserves_proposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    sponsor, cosponsor = _propose_land_bill(senate_game, resolver)
    sponsor_faction = sponsor.faction
    assert sponsor_faction is not None

    # Act
    AcceptLandBillSponsorshipAction().execute(
        game_id=senate_game.id,
        faction_id=sponsor_faction.id,
        selection={},
        random_resolver=resolver,
    )

    # Assert
    senate_game.refresh_from_db()
    assert senate_game.current_proposal is not None
    cosponsor.refresh_from_db()
    assert cosponsor.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)


@pytest.mark.django_db
def test_both_accept_clears_consent_required(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    sponsor, cosponsor = _propose_land_bill(senate_game, resolver)
    sponsor_faction = sponsor.faction
    cosponsor_faction = cosponsor.faction
    assert sponsor_faction is not None
    assert cosponsor_faction is not None

    # Act
    AcceptLandBillSponsorshipAction().execute(
        game_id=senate_game.id,
        faction_id=sponsor_faction.id,
        selection={},
        random_resolver=resolver,
    )
    AcceptLandBillSponsorshipAction().execute(
        game_id=senate_game.id,
        faction_id=cosponsor_faction.id,
        selection={},
        random_resolver=resolver,
    )

    # Assert
    senate_game.refresh_from_db()
    assert senate_game.current_proposal is not None
    assert not Senator.objects.filter(
        game=senate_game, status_items__contains="consent required"
    ).exists()


@pytest.mark.django_db
def test_sponsor_refuse_clears_proposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    sponsor, _ = _propose_land_bill(senate_game, resolver)
    sponsor_faction = sponsor.faction
    assert sponsor_faction is not None

    # Act
    RefuseLandBillSponsorshipAction().execute(
        game_id=senate_game.id,
        faction_id=sponsor_faction.id,
        selection={},
        random_resolver=resolver,
    )

    # Assert
    senate_game.refresh_from_db()
    assert senate_game.current_proposal is None or senate_game.current_proposal == ""
    assert not Senator.objects.filter(
        game=senate_game, status_items__contains="consent required"
    ).exists()


@pytest.mark.django_db
def test_cosponsor_refuse_clears_proposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    sponsor, cosponsor = _propose_land_bill(senate_game, resolver)
    cosponsor_faction = cosponsor.faction
    assert cosponsor_faction is not None

    AcceptLandBillSponsorshipAction().execute(
        game_id=senate_game.id,
        faction_id=sponsor.faction.id,
        selection={},
        random_resolver=resolver,
    )

    # Act
    RefuseLandBillSponsorshipAction().execute(
        game_id=senate_game.id,
        faction_id=cosponsor_faction.id,
        selection={},
        random_resolver=resolver,
    )

    # Assert
    senate_game.refresh_from_db()
    assert senate_game.current_proposal is None or senate_game.current_proposal == ""
    assert not Senator.objects.filter(
        game=senate_game, status_items__contains="consent required"
    ).exists()
