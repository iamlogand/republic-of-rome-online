import { useEffect, useState } from "react"
import Image from "next/image"
import {
  Button,
  Dialog,
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

interface FaceMortalityDialogProps {
  open: boolean
  setOpen: (open: boolean) => void
  onClose: () => void
  actions: Collection<Action>
}

// Action dialog allows the player to ready up for mortality
const FaceMortalityDialog = ({
  open,
  setOpen,
  onClose,
  actions,
}: FaceMortalityDialogProps) => {
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
    const requiredAction = actions.asArray.find((a) => a.required === true)
    if (requiredAction) setRequiredAction(requiredAction)
  }, [actions])

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
      setOpen(false)
    }
  }

  return (
    <Dialog onClose={onClose} open={open} className="m-0">
      <DialogTitle>Ready to Face Mortality?</DialogTitle>
      <div className="absolute right-2 top-2">
        <IconButton aria-label="close" onClick={() => setOpen(false)}>
          <CloseIcon />
        </IconButton>
      </div>

      <DialogContent dividers className="flex flex-col gap-4">
        <blockquote>
          “Death is the wish of some, the relief of many, and the end of all.”
          <cite>Seneca the Younger</cite>
        </blockquote>

        <div>
          <div style={{ float: "left", marginRight: 8 }}>
            <Image src={DeadIcon} alt="Skull and crossbones icon" height={70} />
          </div>
          <p>
            One or more Senators may randomly die. When a Family Senator dies,
            their Heir may appear later as an Unaligned Senator. When a
            Statesman dies, they never return.
          </p>
        </div>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleSubmit}>I&apos;m ready</Button>
      </DialogActions>
    </Dialog>
  )
}

export default FaceMortalityDialog
