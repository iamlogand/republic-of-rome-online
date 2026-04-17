from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models import Senator


def consular_election_proposal_available(game_state) -> bool:
    return not any(
        s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
        for s in game_state.senators
    )


def censor_election_proposal_available(game_state) -> bool:
    return not any(
        f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
        for f in game_state.factions
    )


def dictator_election_proposal_available(game_state) -> bool:
    return censor_election_proposal_available(game_state)


def awarding_concession_proposal_available(game_state) -> bool:
    return len(game_state.game.available_concessions) > 0


def raising_forces_proposal_available(game_state) -> bool:
    return (
        game_state.game.state_treasury >= 10
        and len(game_state.legions) + len(game_state.fleets) < 50
    )


def deploying_forces_proposal_available(game_state) -> bool:
    consul_available = any(
        s
        for s in game_state.senators
        if s.faction
        and s.alive
        and s.location == "Rome"
        and (
            s.has_title(Senator.Title.ROME_CONSUL)
            or s.has_title(Senator.Title.FIELD_CONSUL)
        )
    )
    dictator_available = any(
        s
        for s in game_state.senators
        if s.faction and s.alive and s.location == "Rome"
        and s.has_title(Senator.Title.DICTATOR)
    )
    master_of_horse_exists = any(
        s for s in game_state.senators if s.has_title(Senator.Title.MASTER_OF_HORSE)
    )
    if not consul_available and not (dictator_available and master_of_horse_exists):
        return False
    available_legions = [l for l in game_state.legions if l.campaign is None]
    available_fleets = [f for f in game_state.fleets if f.campaign is None]
    return bool(available_legions or available_fleets)


def recalling_forces_proposal_available(game_state) -> bool:
    proconsul_ids = [
        s.id for s in game_state.senators if s.has_title(Senator.Title.PROCONSUL)
    ]
    recallable_campaigns = [
        c
        for c in game_state.campaigns
        if (c.commander_id is None or c.commander_id in proconsul_ids)
        and not c.recently_deployed
        and not c.recently_reinforced
    ]
    return bool(recallable_campaigns)


def reinforcing_proconsul_proposal_available(game_state) -> bool:
    reinforceable_campaigns = [
        c
        for c in game_state.campaigns
        if c.commander is not None and not c.recently_deployed
    ]
    if not reinforceable_campaigns:
        return False
    available_legions = [l for l in game_state.legions if l.campaign is None]
    available_fleets = [f for f in game_state.fleets if f.campaign is None]
    return bool(available_legions or available_fleets)


def replacing_proconsul_proposal_available(game_state) -> bool:
    proconsul_ids = [
        s.id for s in game_state.senators if s.has_title(Senator.Title.PROCONSUL)
    ]
    replaceable_campaigns = [
        c
        for c in game_state.campaigns
        if c.commander_id is not None
        and c.commander_id in proconsul_ids
        and not c.recently_deployed
        and not c.recently_reinforced
    ]
    if not replaceable_campaigns:
        return False
    dictator_available = any(
        s
        for s in game_state.senators
        if s.faction and s.alive and s.location == "Rome"
        and s.has_title(Senator.Title.DICTATOR)
    )
    master_of_horse_exists = any(
        s for s in game_state.senators if s.has_title(Senator.Title.MASTER_OF_HORSE)
    )
    consul_available = any(
        s
        for s in game_state.senators
        if s.faction
        and s.alive
        and s.location == "Rome"
        and (
            s.has_title(Senator.Title.ROME_CONSUL)
            or s.has_title(Senator.Title.FIELD_CONSUL)
        )
    )
    return bool(consul_available or (dictator_available and master_of_horse_exists))
