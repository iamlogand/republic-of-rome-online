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
import actionDialogStyles from "./ActionDialog.module.css"
import DeadIcon from "@/images/icons/dead.svg"
import request from "@/functions/request"
import { useAuthContext } from "@/contexts/AuthContext"
import { useGameContext } from "@/contexts/GameContext"

interface FaceMortalityDialogProps {
  setOpen: (open: boolean) => void
  actions: Collection<Action>
}

// Action dialog allows the player to ready up for mortality
const FaceMortalityDialog = (props: FaceMortalityDialogProps) => {
  const {
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useAuthContext()
  const { game } = useGameContext()

  const [requiredAction, setRequiredAction] = useState<Action | null>(
    null
  )

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
      <DialogTitle>Ready to Face Mortality?</DialogTitle>
      <IconButton
        aria-label="close"
        className={actionDialogStyles.closeButton}
        onClick={() => props.setOpen(false)}
      >
        <CloseIcon />
      </IconButton>

      <DialogContent dividers className={actionDialogStyles.content}>
        <blockquote>
          “Death is the wish of some, the relief of many, and the end of all.”
          <cite>Seneca the Younger</cite>
        </blockquote>

        <div>
          <div style={{ float: "left", marginRight: 8 }}>
            <Image src={DeadIcon} alt="Skull and crossbones icon" height={70} />
          </div>
          <p>
            One or more senators may randomly die. When a family senator dies,
            their heir may return to play later as an unaligned senator. When a
            statesman dies, they never return.
          </p>
        </div>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleSubmit}>I&apos;m ready</Button>
      </DialogActions>
    </>
  )
}

export default FaceMortalityDialog
