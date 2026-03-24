from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.helpers.end_prosecutions import end_prosecutions
from rorapp.models import Faction, Game, Senator


def finish_prosecution(game_id: int, is_major: bool, guilty: bool) -> None:
    game = Game.objects.get(id=game_id)
    if is_major:
        game.prosecutions_remaining = 0
    else:
        game.prosecutions_remaining = max(0, game.prosecutions_remaining - 1)
    game.current_proposal = None
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()

    factions = list(Faction.objects.filter(game=game_id))
    for faction in factions:
        faction.remove_status_item(FactionStatusItem.DONE)
    Faction.objects.bulk_update(factions, ["status_items"])

    all_senators = list(Senator.objects.filter(game=game_id))
    for senator in all_senators:
        senator.remove_status_item(Senator.StatusItem.ACCUSED)
        senator.remove_status_item(Senator.StatusItem.APPEALED_TO_PEOPLE)
        senator.remove_status_item(Senator.StatusItem.PROSECUTOR)
        senator.remove_status_item(Senator.StatusItem.VOTED_NAY)
        senator.remove_status_item(Senator.StatusItem.VOTED_YEA)
        senator.remove_status_item(Senator.StatusItem.ABSTAINED)
    Senator.objects.bulk_update(all_senators, ["status_items"])

    game = Game.objects.get(id=game_id)
    if game.prosecutions_remaining == 0:
        end_prosecutions(game_id)
