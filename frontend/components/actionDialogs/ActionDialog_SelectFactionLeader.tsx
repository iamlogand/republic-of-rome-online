import { useState } from "react"
import {
  Button,
  Dialog,
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
import TermLink from "@/components/TermLink"

interface SelectFactionLeaderDialogProps {
  onClose: () => void
  actions: Collection<Action>
}

// Action dialog content that displays a list of senators to choose from to be the faction leader
const SelectFactionLeaderDialog = ({
  onClose,
  actions,
}: SelectFactionLeaderDialogProps) => {
  const {
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useCookieContext()
  const { game, allSenators, allFactions, allTitles, dialog, setDialog } =
    useGameContext()

  const requiredAction =
    actions.asArray.find((a) => a.required === true) ?? null
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
      setDialog(null)
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
      <Dialog onClose={onClose} open={dialog === "action"} className="m-0">
        <DialogTitle>Select your Faction Leader</DialogTitle>
        <div className="absolute right-2 top-2">
          <IconButton aria-label="close" onClick={() => setDialog(null)}>
            <CloseIcon />
          </IconButton>
        </div>

        <DialogContent dividers className="flex flex-col gap-4">
          <p>
            Your Faction Leader will be immune from Persuasion Attempts. In the
            unfortunate event of the death of your Faction Leader, his heir will
            immediately assume the role of Faction Leader within your{" "}
            <TermLink name="Faction" />.
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
      </Dialog>
    )
  } else {
    return null
  }
}

export default SelectFactionLeaderDialog
