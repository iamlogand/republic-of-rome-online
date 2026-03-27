from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models import Faction, Game, Log, Senator


def can_propose(game_state, faction, allow_tribune: bool = True) -> bool:
    if any(
        s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
        for s in game_state.senators
    ):
        return False
    has_presiding_magistrate = any(
        s
        for s in game_state.senators
        if s.faction
        and s.faction.id == faction.id
        and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )
    if not allow_tribune:
        return has_presiding_magistrate
    return (
        has_presiding_magistrate
        and not any(
            f
            for f in game_state.factions
            if f.id != faction.id
            and f.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
        )
        or faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    )


def log_proposal(game_id: int, faction: Faction, game: Game, note: str = "") -> None:
    is_tribune_proposal = faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    if is_tribune_proposal:
        faction.remove_status_item(FactionStatusItem.PLAYED_TRIBUNE)
        faction.add_status_item(FactionStatusItem.TRIBUNE_PROPOSAL)
        Log.create_object(
            game_id,
            f"{faction.display_name} used their tribune to propose the motion: {game.current_proposal}.{note}",
        )
    else:
        presiding_magistrate = [
            s
            for s in faction.senators.all()
            if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        ][0]
        Log.create_object(
            game_id,
            f"{presiding_magistrate.display_name} proposed the motion: {game.current_proposal}.{note}",
        )
    faction.add_status_item(FactionStatusItem.PROPOSER)
    faction.save()
