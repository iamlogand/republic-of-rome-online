from typing import Dict, Type
from rorapp.actions import NotDoneAction, DoneAction
from rorapp.actions.meta.action_base import ActionBase


action_registry: Dict[str, Type[ActionBase]] = {
    NotDoneAction.NAME: NotDoneAction,
    DoneAction.NAME: DoneAction,
}
