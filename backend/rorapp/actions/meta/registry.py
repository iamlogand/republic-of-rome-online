from typing import Dict, Type
from rorapp.actions import *
from rorapp.actions.meta.action_base import ActionBase


action_registry: Dict[str, Type[ActionBase]] = {
    AttractKnightAction.NAME: AttractKnightAction,
    ContributeAction.NAME: ContributeAction,
    DoneAction.NAME: DoneAction,
    FactionLeaderChangeAction.NAME: FactionLeaderChangeAction,
    FactionLeaderKeepAction.NAME: FactionLeaderKeepAction,
    FactionLeaderSelectAction.NAME: FactionLeaderSelectAction,
    DoneNotAction.NAME: DoneNotAction,
    InitiativeAuctionPayAction.NAME: InitiativeAuctionPayAction,
    InitiativeAuctionBidAction.NAME: InitiativeAuctionBidAction,
    ProposeConsulsAction.NAME: ProposeConsulsAction,
    SkipAction.NAME: SkipAction,
    SponsorGamesAction.NAME: SponsorGamesAction,
    TransferTalentsAction.NAME: TransferTalentsAction,
}
