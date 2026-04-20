from rorapp.models import Faction, Senator


def faction_has_tribune(faction, senators) -> bool:
    """True if faction has a tribune card or any senator in the faction has a free tribune."""
    if faction.has_card("tribune"):
        return True
    return any(
        s.has_status_item(Senator.StatusItem.FREE_TRIBUNE)
        for s in senators
        if s.faction_id == faction.id
    )


def spend_tribune(game_id: int, faction_id: int) -> None:
    """Spend free tribune if available, otherwise spend a tribune card."""
    senators = list(Senator.objects.filter(game_id=game_id, faction_id=faction_id))
    for senator in senators:
        if senator.has_status_item(Senator.StatusItem.FREE_TRIBUNE):
            senator.remove_status_item(Senator.StatusItem.FREE_TRIBUNE)
            senator.save()
            return
    faction = Faction.objects.get(game=game_id, id=faction_id)
    faction.remove_card("tribune")
    faction.save()
