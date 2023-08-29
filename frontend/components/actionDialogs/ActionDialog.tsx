import React from "react"
import { Dialog } from "@mui/material"

import Collection from "@/classes/Collection"
import PotentialAction from "@/classes/PotentialAction"
import gamePageStyles from "@/components/GamePage.module.css"
import SelectFactionLeaderDialog from "./ActionDialog_SelectFactionLeader"

interface ActionDialogProps {
  potentialActions: Collection<PotentialAction>
  open: boolean
  setOpen: (open: boolean) => void
  onClose: () => void
}

// Dialog box that displays the action that the player must take
const ActionDialog = (props: ActionDialogProps) => {
  const requiredAction = props.potentialActions.asArray.find(a => a.required === true)
  if (requiredAction) {
    return (
      <Dialog onClose={props.onClose} open={props.open} className={gamePageStyles.play}>
        { requiredAction.type === "select_faction_leader" &&
          <SelectFactionLeaderDialog setOpen={props.setOpen} potentialActions={props.potentialActions} />
        }
      </Dialog>
    )
  } else {
    return null
  }
}

export default ActionDialog
