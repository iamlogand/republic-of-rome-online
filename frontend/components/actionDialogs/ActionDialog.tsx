import React from "react"
import { Dialog } from "@mui/material"

import Collection from "@/classes/Collection"
import Action from "@/classes/Action"
import SelectFactionLeaderDialog from "./ActionDialog_SelectFactionLeader"
import FaceMortalityDialog from "./ActionDialog_FaceMortality"
import InitiateSituationDialog from "./ActionDialog_InitiateSituation"

interface ActionDialogProps {
  actions: Collection<Action>
  open: boolean
  setOpen: (open: boolean) => void
  onClose: () => void
}

const dialogs: { [key: string]: React.ComponentType<any> } = {
  select_faction_leader: SelectFactionLeaderDialog,
  face_mortality: FaceMortalityDialog,
  initiate_situation: InitiateSituationDialog,
}

// Dialog box that displays the action that the player must take
const ActionDialog = (props: ActionDialogProps) => {
  const requiredAction = props.actions.asArray.find((a) => a.required === true)
  if (requiredAction) {
    const ContentComponent = dialogs[requiredAction.type]

    return (
      <Dialog onClose={props.onClose} open={props.open} className="m-0">
        <ContentComponent setOpen={props.setOpen} actions={props.actions} />
      </Dialog>
    )
  } else {
    return null
  }
}

export default ActionDialog
