import Image from "next/image"
import { Alert } from "@mui/material"
import MilitaryIcon from "@/images/icons/military.svg"
import ActionLog from "@/classes/ActionLog"
import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import FactionLink from "../FactionLink"
import Faction from "@/classes/Faction"
import { capitalize } from "@mui/material/utils"

interface NotificationProps {
  notification: ActionLog
}

// Notification for when a new war appears during the forum phase
const NewWarNotification = ({ notification }: NotificationProps) => {
  const { allFactions, wars } = useGameContext()

  // Get notification-specific data
  const newWar: War | null = notification.data
    ? wars.byId[notification.data.war] ?? null
    : null
  const initialStatus = notification.data
    ? notification.data.initial_status
    : null
  const initiatingFaction: Faction | null = notification.data
    ? allFactions.byId[notification.data.initiating_faction] ?? null
    : null
  const matchingWars = notification.data
    ? notification.data.matching_wars ?? []
    : []
  const isMatchedByMultiple = matchingWars.length > 1

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={MilitaryIcon} alt="War Icon" width={30} height={30} />
    </div>
  )

  const getStatusAndExplanation = () => {
    switch (initialStatus) {
      case "imminent":
        return `Imminent due to ${
          isMatchedByMultiple ? "Matching Wars" : "a Matching War"
        }`
      default:
        return capitalize(initialStatus)
    }
  }

  if (!newWar || !initiatingFaction) return null

  return (
    <Alert icon={getIcon()}>
      <b>New {capitalize(initialStatus)} War</b>
      <p>
        Rome faces a new threat in the {newWar.getName()}. This War is{" "}
        {getStatusAndExplanation()}.{" "}
        <i>
          Situation initiated by <FactionLink faction={initiatingFaction} />
        </i>
        .
      </p>
    </Alert>
  )
}

export default NewWarNotification
