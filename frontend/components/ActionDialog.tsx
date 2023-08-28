import React from "react"
import { Dialog, DialogTitle } from "@mui/material"

import Collection from "@/classes/Collection"
import PotentialAction from "@/classes/PotentialAction"
import Actions from "@/data/actions.json"
import ActionsType from "@/types/actions"
import SenatorsList from "@/components/SenatorList"
import gamePageStyles from "@/components/GamePage.module.css"
import { useAuthContext } from "@/contexts/AuthContext"
import { useGameContext } from "@/contexts/GameContext"

const typedActions: ActionsType = Actions;

interface ActionDialogProps {
  potentialActions: Collection<PotentialAction>
  open: boolean
  onClose: () => void
}

const ActionDialog = (props: ActionDialogProps) => {
  const { user } = useAuthContext()
  const { allFactions } = useGameContext()
  
  const requiredAction = props.potentialActions.asArray.find(a => a.required === true)

  if (requiredAction) {
    const faction = allFactions.asArray.find(f => f.id === requiredAction.faction)
    return (
      <Dialog onClose={props.onClose} open={props.open} className={gamePageStyles.play}>
        <DialogTitle>{typedActions[requiredAction.type]["title"]}</DialogTitle>
        <SenatorsList faction={faction} height={400} />
      </Dialog>
    )
  } else {
    return null
  }
}

export default ActionDialog
