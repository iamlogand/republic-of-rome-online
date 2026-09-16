from typing import List, Optional

from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Game, Legion, Senator


def army_strength(legions: List[Legion], military: int) -> int:
    """Strength of an army, with the commander's Military rating capped by it (1.11.37)."""

    legion_strength = sum(l.strength for l in legions)
    return legion_strength + min(military, legion_strength)


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
    """The next land victor to declare, if he belongs to this faction (1.11.3)."""

    game = game_state.game
    if (
        game.phase != Game.Phase.REVOLUTION
        or game.sub_phase != Game.SubPhase.CIVIL_WAR_DECLARATION
    ):
        return None
    victors = land_victors_in_declaration_order(game_state)
    if victors and victors[0].commander and victors[0].commander.faction_id == faction_id:
        return victors[0]
    return None


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
    civil_war = next(
        (w for w in game_state.wars if w.primary_rebel_id == rebel.id), None
    )
    legions = [l for l in game_state.legions if l.campaign_id == campaign.id]
    return (
        civil_war is not None
        and army_strength(legions, commander.military) > civil_war.land_strength
    )
