import { useState } from "react"
import { Button, Card, DialogActions, DialogContent, DialogTitle, IconButton } from "@mui/material"

import SenatorsList from "@/components/SenatorList"
import { useGameContext } from "@/contexts/GameContext"
import PotentialAction from "@/classes/PotentialAction"
import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faXmark } from "@fortawesome/free-solid-svg-icons"
import actionDialogStyles from "./ActionDialog.module.css"

interface SelectFactionLeaderDialogProps {
  setOpen: (open: boolean) => void
  potentialActions: Collection<PotentialAction>
}

// Action dialog content that displays a list of senators to choose from to be the faction leader
const SelectFactionLeaderDialog = (props: SelectFactionLeaderDialogProps ) => {
  const { allFactions } = useGameContext()
  const [selectedSenator, setSelectedSenator] = useState<Senator | null>(null)

  const requiredAction = props.potentialActions.asArray.find(a => a.required === true)
  
  if (requiredAction) {
    const faction = allFactions.asArray.find(f => f.id === requiredAction?.faction)
    return (
      <>
        <DialogTitle>Select your Faction Leader ({faction?.getName()} Faction)</DialogTitle>
        <IconButton aria-label="close" className={actionDialogStyles.closeButton} onClick={() => props.setOpen(false)}>
          <FontAwesomeIcon icon={faXmark} width={16} height={16} />
        </IconButton>
        <DialogContent dividers className={actionDialogStyles.content}>
          <p>
            Your Faction Leader will be immune from persuasion attempts. In the unfortunate event of the death of your Faction Leader, his heir will immediately assume the role of Faction Leader within your Faction*.
          </p>
          <p>
            <small>*Except when executed as a result of a Special Major Prosecution.</small>
          </p>
          <Card variant="outlined">
            <SenatorsList faction={faction} height={360} radioSelectedSenator={selectedSenator} setRadioSelectedSenator={setSelectedSenator} />
          </Card>
        </DialogContent>
        <DialogActions>
          <Button>Select</Button>
        </DialogActions>
      </>
    )
  }
  else {
    return null
  }
}

export default SelectFactionLeaderDialog