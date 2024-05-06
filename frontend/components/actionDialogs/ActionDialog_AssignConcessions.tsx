import { useCallback, useEffect, useState } from "react"
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from "@mui/material"
import CloseIcon from "@mui/icons-material/Close"
import EastIcon from "@mui/icons-material/East"
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff"

import Action from "@/classes/Action"
import Collection from "@/classes/Collection"
import request from "@/functions/request"
import { useCookieContext } from "@/contexts/CookieContext"
import { useGameContext } from "@/contexts/GameContext"
import Senator from "@/classes/Senator"
import Secret from "@/classes/Secret"
import SenatorSelectInput from "@/components/SenatorSelectInput"
import TermLink from "@/components/TermLink"

interface AssignConcessionsDialogProps {
  onClose: () => void
  actions: Collection<Action>
}

// Action dialog allows the player to assign concessions
const AssignConcessionsDialog = ({
  onClose,
  actions,
}: AssignConcessionsDialogProps) => {
  const {
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useCookieContext()
  const { game, dialog, setDialog, allSenators, allSecrets } = useGameContext()
  const [requiredAction, setRequiredAction] = useState<Action | null>(null)
  const [concessionSecrets, setConcessionSecrets] = useState<Secret[]>([])
  const [senators, setSenators] = useState<Collection<Senator>>(
    new Collection<Senator>()
  )
  const [secretSenatorMap, setSecretSenatorMap] = useState<
    Record<number, number | null>
  >([])

  // Set required action
  useEffect(() => {
    const requiredAction = actions.asArray.find((a) => a.required === true)
    if (requiredAction) setRequiredAction(requiredAction)
  }, [actions])

  // Set concession secrets
  useEffect(() => {
    if (game && requiredAction) {
      const secrets = allSecrets.asArray.filter(
        (secret) =>
          secret.faction === requiredAction.faction &&
          secret.type === "concession"
      )
      setConcessionSecrets(secrets)
    }
  }, [game, requiredAction])

  // Set senators
  useEffect(() => {
    if (requiredAction) {
      const senators = allSenators.asArray.filter((senator) =>
        requiredAction?.parameters["senators"].includes(senator.id)
      )
      setSenators(new Collection<Senator>(senators))
    }
  }, [requiredAction])

  // Set concession senator map
  useEffect(() => {
    if (concessionSecrets.length > 0 && senators.allIds.length > 0) {
      const map: Record<number, number | null> = {}
      for (let i = 0; i < concessionSecrets.length; i++) {
        map[concessionSecrets[i].id] = null
      }
      setSecretSenatorMap(map)
    }
  }, [concessionSecrets, senators])

  // Handle senator selection
  const handleSenatorSelect = useCallback(
    (secret: Secret, senator: Senator | null) => {
      setSecretSenatorMap((prevState) => {
        const updatedState = { ...prevState }
        updatedState[secret.id] = senator?.id ?? null
        return updatedState
      })
    },
    []
  )

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
        setUser,
        { secret_senator_map: JSON.stringify(secretSenatorMap) }
      )
      setDialog(null)
    }
  }

  return (
    <Dialog onClose={onClose} open={dialog === "action"} className="m-0">
      <DialogTitle>Assign your Concessions</DialogTitle>
      <div className="absolute right-2 top-2">
        <IconButton aria-label="close" onClick={() => setDialog(null)}>
          <CloseIcon />
        </IconButton>
      </div>

      <DialogContent dividers className="flex flex-col gap-4">
        {concessionSecrets.length > 0 ? (
          <>
            <p>
              Each of your Concession Secrets may be revealed to assign the
              respective Concession to a chosen Senator in your Faction.
              Unassigned Concession Secrets will remain hidden in your Faction's
              possession.
            </p>
            <div className="py-2 flex justify-center items-center gap-1 text-purple-600 dark:text-purple-300">
              <VisibilityOffIcon fontSize="small" />{" "}
              <i>Your Secrets are hidden from others</i>
            </div>
            {concessionSecrets.map((secret, index) => {
              const selectedSenatorId = secretSenatorMap[secret.id]
              const selectedSenator = selectedSenatorId
                ? senators.byId[selectedSenatorId]
                : null
              return (
                <div key={index} className="p-2 grid grid-cols-2 gap-4">
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex grow items-center p-4 rounded border-2 border-solid border-purple-600 dark:border-purple-500 shadow-[inset_0_0_10px_2px_hsla(286,72%,60%,0.6)]">
                      <b>{secret.name}</b>
                    </div>
                    <EastIcon fontSize="medium" />
                  </div>
                  <div className="flex items-center">
                    <SenatorSelectInput
                      senators={senators}
                      selectedSenator={selectedSenator}
                      setSelectedSenator={(senator: Senator | null) =>
                        handleSenatorSelect(secret, senator)
                      }
                    />
                  </div>
                </div>
              )
            })}
          </>
        ) : (
          <>
            <p>
              Your <TermLink name="Faction" /> has no Concession Secrets to
              assign at the moment.
            </p>

            <p className="text-purple-600 dark:text-purple-300">
              <i>
                It's important to note that your Faction has at least
                one Secret. Therefore, other players won't be able to determine
                whether you have no Concession Secrets or if you've chosen not
                to assign any.
              </i>
            </p>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleSubmit}>Confirm</Button>
      </DialogActions>
    </Dialog>
  )
}

export default AssignConcessionsDialog
