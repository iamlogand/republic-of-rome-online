from typing import Dict, Type
from rorapp.actions import DoneAction, NotDoneAction, TransferTalentsAction
from rorapp.actions.meta.action_base import ActionBase


action_registry: Dict[str, Type[ActionBase]] = {
    NotDoneAction.NAME: NotDoneAction,
    DoneAction.NAME: DoneAction,
    TransferTalentsAction.NAME: TransferTalentsAction,
}
