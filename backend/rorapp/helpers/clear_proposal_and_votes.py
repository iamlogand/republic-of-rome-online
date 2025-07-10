from rorapp.models import Faction, Game, Senator


def clear_proposal_and_votes(game_id: int):

    game = Game.objects.get(id=game_id)
    game.current_proposal = None
    game.votes_nay = 0
    game.votes_yea = 0
    game.save()

    factions = Faction.objects.filter(game=game_id)
    for faction in factions:
        faction.remove_status_item(Faction.StatusItem.DONE)

    senators = Senator.objects.filter(game=game_id)
    for senator in senators:
        senator.remove_status_item(Senator.StatusItem.VOTED_NAY)
        senator.remove_status_item(Senator.StatusItem.VOTED_YEA)
        senator.remove_status_item(Senator.StatusItem.ABSTAINED)
