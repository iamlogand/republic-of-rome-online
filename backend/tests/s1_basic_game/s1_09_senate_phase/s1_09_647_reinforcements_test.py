import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Game, Legion, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


def _setup_pass_proposal(game: Game, proposal: str):
    game.refresh_from_db()
    game.current_proposal = proposal
    game.votes_yea = 15
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())


@pytest.mark.django_db
def test_forces_added_to_campaign_on_reinforcement(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    proconsul = Senator.objects.get(game=game, family_name="Julius")
    war = game.wars.get(name="1st Punic War")

    deployed_legions = [Legion.objects.create(game=game, number=i) for i in range(1, 6)]
    reserve_legions = [Legion.objects.create(game=game, number=i) for i in range(6, 11)]

    campaign = Campaign.objects.get(game=game)
    for legion in deployed_legions:
        legion.campaign = campaign
        legion.save()

    # Act
    _setup_pass_proposal(
        game,
        "Reinforce Julius' campaign with 5 legions (VI, VII, VIII, IX, X) in the 1st Punic War",
    )

    # Assert
    campaign.refresh_from_db()
    for legion in deployed_legions + reserve_legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id


@pytest.mark.django_db
def test_recently_deployed_campaign_cannot_be_reinforced(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    reserve_legions = [Legion.objects.create(game=game, number=i) for i in range(6, 11)]

    campaign = Campaign.objects.get(game=game)
    campaign.recently_deployed = True
    campaign.save()

    # Act
    _setup_pass_proposal(
        game,
        "Reinforce Julius' campaign with 5 legions (VI, VII, VIII, IX, X) in the 1st Punic War",
    )

    # Assert
    for legion in reserve_legions:
        legion.refresh_from_db()
        assert legion.campaign_id is None


@pytest.mark.django_db
def test_recently_reinforced_campaign_can_be_reinforced_again(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    first_batch = [Legion.objects.create(game=game, number=i) for i in range(1, 6)]
    second_batch = [Legion.objects.create(game=game, number=i) for i in range(6, 11)]
    third_batch = [Legion.objects.create(game=game, number=i) for i in range(11, 16)]

    campaign = Campaign.objects.get(game=game)
    campaign.recently_reinforced = True
    campaign.save()
    for legion in first_batch:
        legion.campaign = campaign
        legion.save()

    _setup_pass_proposal(game, "Reinforce Julius' campaign with 5 legions (VI, VII, VIII, IX, X) in the 1st Punic War")

    # Act
    _setup_pass_proposal(game, "Reinforce Julius' campaign with 5 legions (XI, XII, XIII, XIV, XV) in the 1st Punic War")

    # Assert
    for legion in first_batch + second_batch + third_batch:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id


@pytest.mark.django_db
def test_uncommanded_campaign_cannot_be_reinforced(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    reserve_legions = [Legion.objects.create(game=game, number=i) for i in range(6, 11)]

    campaign = Campaign.objects.get(game=game)
    campaign.commander = None
    campaign.save()

    # Act
    _setup_pass_proposal(
        game,
        "Reinforce uncommanded campaign with 5 legions (VI, VII, VIII, IX, X) in the 1st Punic War",
    )

    # Assert
    for legion in reserve_legions:
        legion.refresh_from_db()
        assert legion.campaign_id is None
