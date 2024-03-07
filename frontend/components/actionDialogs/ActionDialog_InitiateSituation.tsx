import { useEffect, useState } from "react"
import Image from "next/image"
import {
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from "@mui/material"
import CloseIcon from "@mui/icons-material/Close"

import Action from "@/classes/Action"
import Collection from "@/classes/Collection"
import DeadIcon from "@/images/icons/dead.svg"
import request from "@/functions/request"
import { useCookieContext } from "@/contexts/CookieContext"
import { useGameContext } from "@/contexts/GameContext"

interface InitiateSituationDialogProps {
  setOpen: (open: boolean) => void
  actions: Collection<Action>
}

// Action dialog allows the player to ready up for mortality
const InitiateSituationDialog = (props: InitiateSituationDialogProps) => {
  const {
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useCookieContext()
  const { game } = useGameContext()

  const [requiredAction, setRequiredAction] = useState<Action | null>(null)

  // Set required action
  useEffect(() => {
    const requiredAction = props.actions.asArray.find(
      (a) => a.required === true
    )
    if (requiredAction) setRequiredAction(requiredAction)
  }, [props.actions])

  // Handle dialog submission
  const handleSubmit = async () => {
    if (game && requiredAction) {
      request(
        "POST",
        `games/${game.id}/submit-action/${requiredAction.id}/`,
        accessToken,
        refreshToken,
        setAccessToken,
        setRefreshToken,
        setUser
      )
      props.setOpen(false)
    }
  }

  return (
    <>
      <DialogTitle>Initiate a Situation</DialogTitle>
      <div className="absolute right-2 top-2">
        <IconButton aria-label="close" onClick={() => props.setOpen(false)}>
          <CloseIcon />
        </IconButton>
      </div>

      <DialogContent dividers className="flex flex-col gap-4">
        <div>
          <p>
            You must initiate a random Situation. It could be a Secret, a Senator, an Event, a War or an Enemy Leader.
          </p>
          <p className="mt-4 text-sm">This feature is incomplete, so nothing actually happens.</p>
        </div>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleSubmit}>Initiate</Button>
      </DialogActions>
    </>
  )
}

export default InitiateSituationDialog
