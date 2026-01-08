from typing import Dict, Type
from rorapp.actions import *
from rorapp.actions.meta.action_base import ActionBase


action_registry: Dict[str, Type[ActionBase]] = {
    AbstainAction.NAME: AbstainAction,
    AcceptRiskyCommandAction.NAME: AcceptRiskyCommandAction,
    AttractKnightAction.NAME: AttractKnightAction,
    CloseSenateAction.NAME: CloseSenateAction,
    ContributeAction.NAME: ContributeAction,
    DoneAction.NAME: DoneAction,
    DoneNotAction.NAME: DoneNotAction,
    ElectConsulsAction.NAME: ElectConsulsAction,
    FactionLeaderChangeAction.NAME: FactionLeaderChangeAction,
    FactionLeaderKeepAction.NAME: FactionLeaderKeepAction,
    FactionLeaderSelectAction.NAME: FactionLeaderSelectAction,
    InitiativeAuctionBidAction.NAME: InitiativeAuctionBidAction,
    InitiativeAuctionPayAction.NAME: InitiativeAuctionPayAction,
    ProposeDeployingForcesAction.NAME: ProposeDeployingForcesAction,
    ProposeRaisingForcesAction.NAME: ProposeRaisingForcesAction,
    ProposeRecallingForcesAction.NAME: ProposeRecallingForcesAction,
    ProposeReinforcingProconsulAction.NAME: ProposeReinforcingProconsulAction,
    ProposeReplacingProconsulAction.NAME: ProposeReplacingProconsulAction,
    RefuseRiskyCommandAction.NAME: RefuseRiskyCommandAction,
    SelectConsularOfficesAction.NAME: SelectConsularOfficesAction,
    SelectPreferredAttackerAction.NAME: SelectPreferredAttackerAction,
    SelectPreferredConsularOfficeAction.NAME: SelectPreferredConsularOfficeAction,
    SkipAction.NAME: SkipAction,
    SponsorGamesAction.NAME: SponsorGamesAction,
    TransferTalentsAction.NAME: TransferTalentsAction,
    VoteCallFactionAction.NAME: VoteCallFactionAction,
    VoteNayAction.NAME: VoteNayAction,
    VoteYeaAction.NAME: VoteYeaAction,
}
