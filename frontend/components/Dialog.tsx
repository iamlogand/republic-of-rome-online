import React from "react"

import Collection from "@/classes/Collection"
import Action from "@/classes/Action"
import SelectFactionLeaderDialog from "./actionDialogs/ActionDialog_SelectFactionLeader"
import FaceMortalityDialog from "./actionDialogs/ActionDialog_FaceMortality"
import InitiateSituationDialog from "./actionDialogs/ActionDialog_InitiateSituation"

interface ActionDialogProps {
  open: boolean
  setOpen: (open: boolean) => void
  onClose: () => void
  actions: Collection<Action>
}

const dialogs: { [key: string]: React.ComponentType<any> } = {
  select_faction_leader: SelectFactionLeaderDialog,
  face_mortality: FaceMortalityDialog,
  initiate_situation: InitiateSituationDialog,
}

// Dialog box that displays the action that the player must take
const Dialog = ({
  open,
  setOpen,
  onClose,
  actions,
}: ActionDialogProps) => {
  const requiredAction = actions.asArray.find((a) => a.required === true)
  if (requiredAction) {
    const ContentComponent = dialogs[requiredAction.type]

    return (
      <ContentComponent
        open={open}
        setOpen={setOpen}
        onClose={onClose}
        actions={actions}
      />
    )
  } else {
    return null
  }
}

export default Dialog
