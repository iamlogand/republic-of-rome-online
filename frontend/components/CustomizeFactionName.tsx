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
import FactionIcon from "@/components/FactionIcon"
import FactionName from "@/components/FactionName"

interface CustomizeFactionNameProps {
  faction: Faction
}

const CustomizeFactionName = ({ faction }: CustomizeFactionNameProps) => {
  const {
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    user,
    setUser,
  } = useCookieContext()
  const [open, setOpen] = useState<boolean>(false)
  const [name, setName] = useState<string>("")
  const [nameFeedback, setNameFeedback] = useState<string>("")

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Limit the name to 30 characters
    if (event.target.value.length > 30) {
      event.target.value = name
    }
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

  // Create a custom Faction object with the custom name for showing previews
  const customFactionObject = Object.assign(
    Object.create(Object.getPrototypeOf(faction)),
    faction
  )
  customFactionObject.customName = name

  return (
    <>
      <Button variant="outlined" size="small" onClick={() => setOpen(true)}>
        <div className="flex items-center gap-1">
          <EditIcon fontSize="small" />
          Customize
        </div>
      </Button>
      <Dialog onClose={() => setOpen(false)} open={open}>
        <DialogTitle>Customize your Faction&apos;s name</DialogTitle>
        <div className="absolute right-2 top-2">
          <IconButton aria-label="close" onClick={() => setOpen(false)}>
            <CloseIcon />
          </IconButton>
        </div>
        <form onSubmit={handleSubmit}>
          <DialogContent dividers className="flex flex-col gap-4">
            <p>
              You may replace your{" "}
              <TermLink name="Faction" displayName="Faction" />
              &apos;s default name with a custom name. This name will be
              displayed to other players.
            </p>
            <p>
              Once customized, your faction&apos;s name can&apos;t be changed
              again.
            </p>
            <TextField
              id="name"
              label="Name"
              error={nameFeedback != ""}
              onChange={handleNameChange}
              helperText={capitalize(nameFeedback)}
            />
            <div className="flex flex-col gap-1">
              <p className="text-sm">Full name preview</p>
              <div className="p-2 border border-solid rounded border-neutral-200 dark:border-neutral-500">
                <p>
                  <b>
                    <FactionIcon faction={faction} size={17} />{" "}
                    <FactionName faction={customFactionObject} />
                  </b>{" "}
                  <span>
                    {name.length > 0 && (
                      <span>
                        (<FactionName faction={faction} />)
                      </span>
                    )}{" "}
                    of {user?.username}
                  </span>
                </p>
              </div>
            </div>
            <div className="flex flex-col gap-1">
              <p className="text-sm">Short name preview</p>
              <div className="flex gap-1 w-[164px] p-2 border border-solid rounded border-neutral-200 dark:border-neutral-500">
                <b>
                  <FactionIcon faction={faction} size={17} />
                </b>{" "}
                <b>
                  <FactionName faction={customFactionObject} maxWidth={140} />
                </b>
              </div>
            </div>
          </DialogContent>
          <DialogActions>
            <Button type="submit" disabled={name.length === 0}>
              Confirm
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </>
  )
}

export default CustomizeFactionName
