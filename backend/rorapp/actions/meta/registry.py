from typing import Dict, Type
from rorapp.actions import *
from rorapp.actions.meta.action_base import ActionBase


action_registry: Dict[str, Type[ActionBase]] = {
    AbstainAction.NAME: AbstainAction,
    AttractKnightAction.NAME: AttractKnightAction,
    CloseSenateAction.NAME: CloseSenateAction,
    ContributeAction.NAME: ContributeAction,
    AcceptCommandAction.NAME: AcceptCommandAction,
    DoneAction.NAME: DoneAction,
    FactionLeaderChangeAction.NAME: FactionLeaderChangeAction,
    FactionLeaderKeepAction.NAME: FactionLeaderKeepAction,
    FactionLeaderSelectAction.NAME: FactionLeaderSelectAction,
    DoneNotAction.NAME: DoneNotAction,
    InitiativeAuctionPayAction.NAME: InitiativeAuctionPayAction,
    InitiativeAuctionBidAction.NAME: InitiativeAuctionBidAction,
    ElectConsulsAction.NAME: ElectConsulsAction,
    ProposeDeployingForcesAction.NAME: ProposeDeployingForcesAction,
    ProposeRaisingForcesAction.NAME: ProposeRaisingForcesAction,
    RefuseCommandAction.NAME: RefuseCommandAction,
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
