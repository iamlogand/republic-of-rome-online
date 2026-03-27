import pytest
import threading
from rest_framework.test import APIRequestFactory, force_authenticate
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models import AvailableAction, Faction, Game
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.views.submit_action import SubmitActionViewSet


@pytest.mark.django_db(transaction=True)
def test_concurrent_vote_submissions_only_one_succeeds(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.current_proposal = "Test proposal"
    game.save()
    initial_votes_yea = game.votes_yea
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()

    execute_effects_and_manage_actions(game.id)

    vote_yea_action = AvailableAction.objects.get(
        game=game, faction=faction, base_name="Vote yea"
    )

    factory = APIRequestFactory()
    view = SubmitActionViewSet.as_view({"post": "submit_action"})
    results = []

    def submit_vote():
        request = factory.post(
            f"/api/games/{game.id}/submit-action/{vote_yea_action.id}",
            {},
            format="json",
        )
        force_authenticate(request, user=faction.player)
        try:
            response = view(
                request,
                game_id=game.id,
                action_id=vote_yea_action.id,
            )
            results.append(("success", response.status_code))
        except Exception as e:
            results.append(("error", str(e)))

    thread1 = threading.Thread(target=submit_vote)
    thread2 = threading.Thread(target=submit_vote)

    # Act
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Assert
    game.refresh_from_db()
    faction.refresh_from_db()
    faction_votes = sum(s.votes for s in faction.senators.all())
    assert game.votes_yea == initial_votes_yea + faction_votes
    successful_requests = [r for r in results if r[0] == "success" and r[1] == 200]
    assert len(successful_requests) == 1
