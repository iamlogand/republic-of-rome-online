from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.helpers.hrao import highest_ranking_senator
from rorapp.models import Faction, Log, Senator


def handle_unanimous_defeat(game_id: int) -> None:
    factions = list(Faction.objects.filter(game=game_id))

    if any(f.has_status_item(FactionStatusItem.PROPOSED_VIA_TRIBUNE) for f in factions):
        # No penalty for tribune-initiated proposals
        return

    senators = list(Senator.objects.filter(game=game_id))

    presiding_magistrate = next(
        (s for s in senators if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)),
        None,
    )
    if not presiding_magistrate or not presiding_magistrate.faction_id:
        return

    senators_from_other_factions = [
        s
        for s in senators
        if s.faction_id
        and s.faction_id != presiding_magistrate.faction_id
        and s.location == "Rome"
        and s.alive
    ]
    if not senators_from_other_factions:
        return

    if not all(
        s.has_status_item(Senator.StatusItem.VOTED_NAY)
        for s in senators_from_other_factions
    ):
        return

    if presiding_magistrate.influence == 0:
        Log.create_object(
            game_id,
            f"The proposal was unanimously defeated. With no influence left to lose, {presiding_magistrate.display_name} stepped down as presiding magistrate.",
        )
        _do_step_down(game_id, presiding_magistrate, senators)
    else:
        Log.create_object(
            game_id,
            f"The proposal was unanimously defeated. {presiding_magistrate.display_name} must lose 1 influence or step down.",
        )
        presiding_magistrate.add_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
        presiding_magistrate.save()


def step_down_by_choice(game_id: int, senator_id: int) -> None:
    senators = list(Senator.objects.filter(game=game_id))
    senator = next(s for s in senators if s.id == senator_id)

    Log.create_object(
        game_id,
        f"{senator.display_name} decided to step down as presiding magistrate.",
    )

    _do_step_down(game_id, senator, senators)


def _do_step_down(game_id: int, presiding_magistrate: Senator, senators: list) -> None:
    presiding_magistrate.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
    presiding_magistrate.remove_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
    presiding_magistrate.add_status_item(Senator.StatusItem.STEPPED_DOWN)
    presiding_magistrate.save()

    candidates = [
        s
        for s in senators
        if s.id != presiding_magistrate.id
        and s.faction_id
        and s.alive
        and s.location == "Rome"
    ]
    next_presiding_magistrate = highest_ranking_senator(
        candidates, exclude_stepped_down=True
    )
    if not next_presiding_magistrate:
        return

    next_presiding_magistrate.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    next_presiding_magistrate.save()

    Log.create_object(
        game_id,
        f"{next_presiding_magistrate.display_name} took over as presiding magistrate.",
    )
