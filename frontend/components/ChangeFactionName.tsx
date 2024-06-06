import { useState } from "react"
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from "@mui/material"
import EditIcon from "@mui/icons-material/Edit"
import CloseIcon from "@mui/icons-material/Close"
import TextField from "@mui/material/TextField"
import { capitalize } from "@mui/material/utils"
import Faction from "@/classes/Faction"
import request from "@/functions/request"

import TermLink from "@/components/TermLink"
import { useCookieContext } from "@/contexts/CookieContext"

interface CustomizeFactionNameProps {
  faction: Faction
}

const CustomizeFactionName = ({ faction }: CustomizeFactionNameProps) => {
  const {
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useCookieContext()
  const [open, setOpen] = useState<boolean>(false)
  const [name, setName] = useState<string>("")
  const [nameFeedback, setNameFeedback] = useState<string>("")

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setName(event.target.value)
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const response = await request(
      "PATCH",
      "factions/" + faction.id + "/",
      accessToken,
      refreshToken,
      setAccessToken,
      setRefreshToken,
      setUser,
      { custom_name: name }
    )

    if (response) {
      if (response.status === 200) {
        setOpen(false)
      } else {
        if (response.data) {
          if (
            response.data.custom_name &&
            Array.isArray(response.data.custom_name) &&
            response.data.custom_name.length > 0
          ) {
            setNameFeedback(response.data.custom_name[0])
          } else {
            setNameFeedback("")
          }
        }
      }
    }
  }

  return (
    <>
      <Button variant="outlined" size="small" onClick={() => setOpen(true)}>
        <div className="flex items-center gap-1">
          <EditIcon fontSize="small" />
          Customize
        </div>
      </Button>
      <Dialog onClose={() => setOpen(false)} open={open}>
        <DialogTitle>Customize your Faction's name</DialogTitle>
        <div className="absolute right-2 top-2">
          <IconButton aria-label="close" onClick={() => setOpen(false)}>
            <CloseIcon />
          </IconButton>
        </div>
        <form onSubmit={handleSubmit}>
          <DialogContent dividers className="flex flex-col gap-4">
            <p>
              You may replace "{faction.getName()} Faction" with a custom{" "}
              <TermLink name="Faction" displayName="Faction" /> name. This name
              will be displayed to other players.
            </p>
            <p>Once customized, your faction's name can't be changed again.</p>
            <TextField
              required
              id="name"
              label="Name"
              error={nameFeedback != ""}
              onChange={handleNameChange}
              helperText={capitalize(nameFeedback)}
            />
          </DialogContent>
          <DialogActions>
            <Button type="submit">Confirm</Button>
          </DialogActions>
        </form>
      </Dialog>
    </>
  )
}

export default CustomizeFactionName
