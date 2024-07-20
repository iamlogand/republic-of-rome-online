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
import Image from "next/image"

import Action from "@/classes/Action"
import Collection from "@/classes/Collection"
import request from "@/functions/request"
import { useCookieContext } from "@/contexts/CookieContext"
import { useGameContext } from "@/contexts/GameContext"
import Senator from "@/classes/Senator"
import Secret from "@/classes/Secret"
import SenatorSelector from "@/components/SenatorSelector"
import TermLink from "@/components/TermLink"
import SecretsIcon from "@/images/icons/secrets.svg"
import TalentsAmount from "../TalentsAmount"
import ConcessionTermLink from "@/components/ConcessionTermLink"

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

  // Set senators and concession secrets
  useEffect(() => {
    if (requiredAction) {
      const senators = allSenators.asArray.filter((senator) =>
        requiredAction?.parameters["senators"].includes(senator.id)
      )
      setSenators(new Collection<Senator>(senators))
      const secrets = allSecrets.asArray.filter((secret) =>
        requiredAction?.parameters["concession_secrets"].includes(secret.id)
      )
      setConcessionSecrets(secrets)
    }
  }, [requiredAction, allSenators, allSecrets])

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

  const renderSecretDescription = (secretName: string) => {
    let amount = 2
    let trigger = null
    if (secretName === "Armaments") {
      amount = 2
      trigger = "Legion"
    }
    if (secretName === "Ship Building") {
      amount = 3
      trigger = "Fleet"
    }
    if (secretName === "Aegyptian Grain") {
      amount = 5
    }
    if (secretName === "Sicilian Grain") {
      amount = 4
    }
    if (["Harbor Fees", "Mining"].includes(secretName)) {
      amount = 3
    }
    return (
      <span>
        <TalentsAmount amount={amount} sign="+" />{" "}
        {trigger ? (
          <span>per {trigger} Raised</span>
        ) : (
          <TermLink name="Personal Revenue" hiddenUnderline />
        )}
      </span>
    )
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
              Each of your <TermLink name="Concession" />{" "}
              <TermLink name="Secret" plural /> may be revealed to assign the
              respective Concession to a chosen <TermLink name="Senator" /> in
              your <TermLink name="Faction" />. Unassigned Concession Secrets
              will remain hidden in your Faction&apos;s possession.
            </p>
            <div className="py-2 flex justify-center items-center gap-1 text-purple-600 dark:text-purple-300">
              <Image src={SecretsIcon} alt={"g"} width={26} height={26} />
              <i>Your Secrets are hidden from others</i>
            </div>
            {concessionSecrets.map((secret, index) => {
              if (!secret || !secret.name) return null
              const selectedSenatorId = secretSenatorMap[secret.id]
              const selectedSenator = selectedSenatorId
                ? senators.byId[selectedSenatorId]
                : null
              return (
                <div key={index} className="p-2 grid grid-cols-2 gap-4">
                  <div className="flex items-center justify-between gap-4">
                    <div
                      className={
                        "px-4 h-[70px] box-border flex flex-col grow items-center justify-center gap-1 rounded \
                        border-2 border-solid border-purple-500 shadow-[inset_0_0_10px_2px_hsla(286,72%,60%,0.6)]"
                      }
                    >
                      <b>
                        <ConcessionTermLink
                          name={secret.name}
                          hiddenUnderline
                        />
                      </b>
                      {renderSecretDescription(secret.name)}
                    </div>
                    <EastIcon fontSize="medium" />
                  </div>
                  <div className="flex items-center">
                    <SenatorSelector
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
              Your <TermLink name="Faction" /> has no Concession{" "}
              <TermLink name="Secret" plural /> to assign at the moment.
            </p>

            <p className="text-purple-600 dark:text-purple-300">
              <i>
                Since your Faction has at least one Secret, other players
                won&apos;t be able to determine whether you have no Concession
                Secrets or if you&apos;ve chosen not to assign any.
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
