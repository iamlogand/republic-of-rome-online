from typing import Dict, Type
from rorapp.actions import *
from rorapp.actions.meta.action_base import ActionBase


action_registry: Dict[str, Type[ActionBase]] = {
    ContributeAction.NAME: ContributeAction,
    DoneAction.NAME: DoneAction,
    FactionLeaderChangeAction.NAME: FactionLeaderChangeAction,
    FactionLeaderKeepAction.NAME: FactionLeaderKeepAction,
    FactionLeaderSelectAction.NAME: FactionLeaderSelectAction,
    NotDoneAction.NAME: NotDoneAction,
    TransferTalentsAction.NAME: TransferTalentsAction,
    SkipAction.NAME: SkipAction,
    SponsorGamesAction.NAME: SponsorGamesAction,
}
