import { useEffect, useState } from "react"
import { Alert, Button, Card, DialogActions, DialogContent, DialogTitle, IconButton, Snackbar } from "@mui/material"

import SenatorsList from "@/components/SenatorList"
import { useGameContext } from "@/contexts/GameContext"
import PotentialAction from "@/classes/PotentialAction"
import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faXmark } from "@fortawesome/free-solid-svg-icons"
import actionDialogStyles from "./ActionDialog.module.css"
import { useAuthContext } from "@/contexts/AuthContext"
import request from "@/functions/request"

interface SelectFactionLeaderDialogProps {
  setOpen: (open: boolean) => void
  potentialActions: Collection<PotentialAction>
}

// Action dialog content that displays a list of senators to choose from to be the faction leader
const SelectFactionLeaderDialog = (props: SelectFactionLeaderDialogProps ) => {
  const { accessToken, refreshToken, setAccessToken, setRefreshToken, setUser } = useAuthContext()
  const { game, allSenators, allFactions, allTitles } = useGameContext()

  const [requiredAction, setRequiredAction] = useState<PotentialAction | null>(null)
  const [selectedSenator, setSelectedSenator] = useState<Senator | null>(null)

  // Set initially selected senator to the current faction leader
  useEffect(() => {
    const senators = allSenators.asArray.filter(s => s.faction === requiredAction?.faction)
    const factionLeaderTitles = allTitles.asArray.filter(t => t.name === "Faction Leader")
    const factionLeader = factionLeaderTitles ? senators.find(s => factionLeaderTitles.some(t => t.senator === s.id)) : null
    if (factionLeader)
      setSelectedSenator(factionLeader)
  }, [requiredAction, allSenators, allTitles, setSelectedSenator])

  // Set required action
  useEffect(() => {
    const requiredAction = props.potentialActions.asArray.find(a => a.required === true)
    if (requiredAction) setRequiredAction(requiredAction)
  }, [props.potentialActions])

  // Handle dialog submission
  const handleSubmit = async () => {
    if (game && requiredAction && selectedSenator) {
      request('POST', `games/${game.id}/submit-action/${requiredAction.id}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser, {"leader_id": selectedSenator.id})
      props.setOpen(false)
    }
  }

  // Disable the submit button if no senator is selected
  const getDisabled = () => {
    if (selectedSenator) return {}
    else return {disabled: true}
  }

  if (requiredAction) {
    const faction = allFactions.byId[requiredAction.faction] ?? null
    return (
      <>
        <DialogTitle>Select your Faction Leader</DialogTitle>
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

          {/* 354 pixels is the height required to show 3 senators */}
          <SenatorsList faction={faction} height={356} radioSelectedSenator={selectedSenator} setRadioSelectedSenator={setSelectedSenator} />
        </DialogContent>

        <DialogActions>
          <Button onClick={handleSubmit} {...getDisabled()}>Select</Button>
        </DialogActions>
      </>
    )
  }
  else {
    return null
  }
}

export default SelectFactionLeaderDialog