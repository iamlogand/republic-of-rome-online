from typing import Dict, Type
from rorapp.actions import *
from rorapp.actions.meta.action_base import ActionBase


action_registry: Dict[str, Type[ActionBase]] = {
    ContributeAction.NAME: ContributeAction,
    DoneAction.NAME: DoneAction,
    NotDoneAction.NAME: NotDoneAction,
    SelectFactionLeaderAction.NAME: SelectFactionLeaderAction,
    TransferTalentsAction.NAME: TransferTalentsAction,
}
