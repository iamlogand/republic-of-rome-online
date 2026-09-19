from typing import List, Optional

from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.force_strength import force_strength
from rorapp.models import Campaign, Game, Legion, Senator


def land_victors_in_declaration_order(
    game_state: GameStateLive | GameStateSnapshot,
) -> List[Campaign]:
    """Land victors starting with the HRAO's faction and proceeding clockwise (1.11.3)."""

    positions = {f.id: f.position for f in game_state.factions}
    hrao = next(
        (s for s in game_state.senators if s.has_title(Senator.Title.HRAO)), None
    )
    start = positions[hrao.faction_id] if hrao and hrao.faction_id else 0

    victors = [
        (positions[c.commander.faction_id], c.id, c)
        for c in game_state.campaigns
        if c.land_victory and c.commander and c.commander.faction_id
    ]
    victors.sort(key=lambda v: (v[0] < start, v[0], v[1]))
    return [c for _, _, c in victors]


def declaring_campaign(
    game_state: GameStateLive | GameStateSnapshot, faction_id: int
) -> Optional[Campaign]:
    """The land victor this faction is deciding for, if it is their turn (1.11.3)."""

    game = game_state.game
    faction = game_state.get_faction(faction_id)
    if (
        game.phase != Game.Phase.REVOLUTION
        or game.sub_phase != Game.SubPhase.REVOLT_DECLARATION
        or not faction
        or not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    ):
        return None
    return next(
        (
            c
            for c in land_victors_in_declaration_order(game_state)
            if c.commander and c.commander.faction_id == faction_id
        ),
        None,
    )


def revolt_available(
    game_state: GameStateLive | GameStateSnapshot, campaign: Campaign
) -> bool:
    """Whether a land victor may declare, given any standing rebel (1.11.3)."""

    commander = campaign.commander
    if not commander:
        return False
    rebel = next((s for s in game_state.senators if s.rebel), None)
    if not rebel:
        return True
    # Only one faction may be in revolt, and once a Primary Rebel has been
    # determined nobody else may revolt (1.11.3)
    if rebel.faction_id == commander.faction_id or not rebel.has_status_item(
        Senator.StatusItem.DECLARED_REVOLT
    ):
        return False
    revolt = next((w for w in game_state.wars if w.primary_rebel_id == rebel.id), None)
    army = sum(l.strength for l in game_state.legions if l.campaign_id == campaign.id)
    return (
        revolt is not None
        and force_strength(army, commander.military) > revolt.land_strength
    )


def rollable_legions(
    game_state: GameStateLive | GameStateSnapshot, campaign: Campaign
) -> List[Legion]:
    """Legions that must roll to follow their commander into revolt (1.11.31)."""

    return sorted(
        (
            l
            for l in game_state.legions
            if l.campaign_id == campaign.id
            and not (l.veteran and l.allegiance_id == campaign.commander_id)
        ),
        key=lambda l: l.number,
    )
