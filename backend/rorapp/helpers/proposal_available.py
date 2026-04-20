from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.helpers.game_data import load_land_bills
from rorapp.models import Senator

_LAND_BILLS = load_land_bills()


def consular_election_proposal_available(game_state) -> bool:
    return not any(
        s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
        for s in game_state.senators
    )


def censor_election_proposal_available(game_state) -> bool:
    return not any(
        f.has_status_item(FactionStatusItem.CALLED_TO_VOTE) for f in game_state.factions
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
        if s.faction
        and s.alive
        and s.location == "Rome"
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
        if s.faction
        and s.alive
        and s.location == "Rome"
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


LAND_BILL_EFFECT = {
    "I": GameEffect.LAND_BILL_1,
    "II": GameEffect.LAND_BILL_2,
    "III": GameEffect.LAND_BILL_3,
}

LAND_BILL_TYPES = [
    (bill_type, LAND_BILL_EFFECT[bill_type], data["max_count"])
    for bill_type, data in _LAND_BILLS.items()
]

LAND_BILL_REPEAL_SPONSOR_POP_REQUIRED = {
    bill_type: data["repeal_sponsor_popularity_required"]
    for bill_type, data in _LAND_BILLS.items()
    if data["recurring"]
}


def land_bill_proposal_available(game_state) -> bool:
    senators_in_rome = [
        s for s in game_state.senators if s.faction and s.alive and s.location == "Rome"
    ]
    if len(senators_in_rome) < 2:
        return False
    game = game_state.game
    for bill_type, effect, max_count in LAND_BILL_TYPES:
        already_proposed = game.has_unavailable_proposal(f"type {bill_type} land bill")
        at_cap = game.count_effect(effect) >= max_count
        if not already_proposed and not at_cap:
            return True
    return False


def land_bill_repeal_proposal_available(game_state) -> bool:
    game = game_state.game
    if game.has_unavailable_proposal(
        "repeal type II land bill"
    ) or game.has_unavailable_proposal("repeal type III land bill"):
        return False
    repealable_types = [
        bill_type
        for bill_type, effect, _ in LAND_BILL_TYPES
        if bill_type != "I" and game.count_effect(effect) > 0
    ]
    if not repealable_types:
        return False
    senators_in_rome = [
        s for s in game_state.senators if s.faction and s.alive and s.location == "Rome"
    ]
    for senator in senators_in_rome:
        for bill_type in repealable_types:
            if senator.popularity >= LAND_BILL_REPEAL_SPONSOR_POP_REQUIRED[bill_type]:
                return True
    return False
