from typing import Dict, Type
from rorapp.actions import (
    ContributeAction,
    DoneAction,
    NotDoneAction,
    TransferTalentsAction,
)
from rorapp.actions.meta.action_base import ActionBase

action_registry: Dict[str, Type[ActionBase]] = {
    ContributeAction.NAME: ContributeAction,
    DoneAction.NAME: DoneAction,
    NotDoneAction.NAME: NotDoneAction,
    TransferTalentsAction.NAME: TransferTalentsAction,
}
