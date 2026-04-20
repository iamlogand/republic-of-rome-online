from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.helpers.proposal_available import (
    awarding_concession_proposal_available,
    censor_election_proposal_available,
    consular_election_proposal_available,
    deploying_forces_proposal_available,
    dictator_election_proposal_available,
    land_bill_proposal_available,
    land_bill_repeal_proposal_available,
    raising_forces_proposal_available,
    recalling_forces_proposal_available,
    reinforcing_proconsul_proposal_available,
    replacing_proconsul_proposal_available,
)
from rorapp.models import Faction, Game, Log, Senator


def senate_open_for_proposals(game_state, sub_phase) -> bool:
    return (
        game_state.game.phase == Game.Phase.SENATE
        and game_state.game.sub_phase == sub_phase
        and (
            game_state.game.current_proposal is None
            or game_state.game.current_proposal == ""
        )
    )


def any_proposal_available(game_state) -> bool:
    sub_phase = game_state.game.sub_phase

    if sub_phase == Game.SubPhase.CONSULAR_ELECTION:
        return consular_election_proposal_available(game_state)

    if sub_phase == Game.SubPhase.CENSOR_ELECTION:
        return censor_election_proposal_available(game_state)

    if sub_phase == Game.SubPhase.DICTATOR_ELECTION:
        return dictator_election_proposal_available(game_state)

    if sub_phase == Game.SubPhase.OTHER_BUSINESS:
        return (
            awarding_concession_proposal_available(game_state)
            or land_bill_proposal_available(game_state)
            or land_bill_repeal_proposal_available(game_state)
            or raising_forces_proposal_available(game_state)
            or deploying_forces_proposal_available(game_state)
            or recalling_forces_proposal_available(game_state)
            or reinforcing_proconsul_proposal_available(game_state)
            or replacing_proconsul_proposal_available(game_state)
        )

    return False


def faction_can_propose(game_state, faction, allow_tribune: bool = True) -> bool:
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
        faction.add_status_item(FactionStatusItem.PROPOSED_VIA_TRIBUNE)
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
    faction.save()
