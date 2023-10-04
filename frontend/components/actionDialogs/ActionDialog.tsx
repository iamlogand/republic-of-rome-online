import React from "react"
import { Dialog } from "@mui/material"

import Collection from "@/classes/Collection"
import PotentialAction from "@/classes/PotentialAction"
import gamePageStyles from "@/components/GamePage.module.css"
import SelectFactionLeaderDialog from "./ActionDialog_SelectFactionLeader"
import FaceMortalityDialog from "./ActionDialog_FaceMortality"

interface ActionDialogProps {
  potentialActions: Collection<PotentialAction>
  open: boolean
  setOpen: (open: boolean) => void
  onClose: () => void
}

const dialogs: { [key: string]: React.ComponentType<any> } = {
  select_faction_leader: SelectFactionLeaderDialog,
  face_mortality: FaceMortalityDialog,
}

// Dialog box that displays the action that the player must take
const ActionDialog = (props: ActionDialogProps) => {
  const requiredAction = props.potentialActions.asArray.find(
    (a) => a.required === true
  )
  if (requiredAction) {
    const ContentComponent = dialogs[requiredAction.type]

    return (
      <Dialog
        onClose={props.onClose}
        open={props.open}
        className={gamePageStyles.play}
      >
        <ContentComponent
          setOpen={props.setOpen}
          potentialActions={props.potentialActions}
        />
      </Dialog>
    )
  } else {
    return null
  }
}

export default ActionDialog
