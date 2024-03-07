import { useState } from "react"
import {
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from "@mui/material"
import CloseIcon from "@mui/icons-material/Close"

import SenatorList from "@/components/SenatorList"
import { useGameContext } from "@/contexts/GameContext"
import Action from "@/classes/Action"
import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import { useCookieContext } from "@/contexts/CookieContext"
import request from "@/functions/request"

interface SelectFactionLeaderDialogProps {
  setOpen: (open: boolean) => void
  actions: Collection<Action>
}

// Action dialog content that displays a list of senators to choose from to be the faction leader
const SelectFactionLeaderDialog = (props: SelectFactionLeaderDialogProps) => {
  const {
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useCookieContext()
  const { game, allSenators, allFactions, allTitles } = useGameContext()

  const requiredAction =
    props.actions.asArray.find((a) => a.required === true) ?? null
  const senators = new Collection<Senator>(
    allSenators.asArray.filter((senator) =>
      requiredAction?.parameters.includes(senator.id)
    )
  )
  const [selectedSenator, setSelectedSenator] = useState<Senator | null>(() => {
    const factionLeaderTitles = allTitles.asArray.filter(
      (t) => t.name === "Faction Leader"
    )
    const factionLeader = factionLeaderTitles
      ? senators.asArray.find(
          (s) => factionLeaderTitles.some((t) => t.senator === s.id) && s.alive
        ) ?? null
      : null
    return factionLeader
  })

  // Handle dialog submission
  const handleSubmit = async () => {
    if (game && requiredAction && selectedSenator) {
      request(
        "POST",
        `games/${game.id}/submit-action/${requiredAction.id}/`,
        accessToken,
        refreshToken,
        setAccessToken,
        setRefreshToken,
        setUser,
        { leader_id: selectedSenator.id }
      )
      props.setOpen(false)
    }
  }

  // Disable the submit button if no senator is selected
  const getDisabled = () => {
    if (selectedSenator) return {}
    else return { disabled: true }
  }

  if (requiredAction) {
    const faction = allFactions.byId[requiredAction.faction] ?? null
    return (
      <>
        <DialogTitle>Select your Faction Leader</DialogTitle>
        <div className="absolute right-2 top-2">
          <IconButton aria-label="close" onClick={() => props.setOpen(false)}>
            <CloseIcon />
          </IconButton>
        </div>

        <DialogContent dividers className="flex flex-col gap-4">
          <p>
            Your Faction Leader will be immune from persuasion attempts. In the
            unfortunate event of the death of your Faction Leader, his heir will
            immediately assume the role of Faction Leader within your Faction*.
          </p>
          <p>
            <small>
              *Except when executed as a result of a Special Major Prosecution.
            </small>
          </p>

          {/* 365 pixels is enough height to show 3 senators */}
          <SenatorList
            faction={faction}
            senators={senators}
            height={371}
            radioSelectedSenator={selectedSenator}
            setRadioSelectedSenator={setSelectedSenator}
            border
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={handleSubmit} {...getDisabled()}>
            Select
          </Button>
        </DialogActions>
      </>
    )
  } else {
    return null
  }
}

export default SelectFactionLeaderDialog
