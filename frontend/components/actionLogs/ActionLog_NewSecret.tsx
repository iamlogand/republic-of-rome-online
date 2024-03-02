import Image from "next/image"
import { Alert } from "@mui/material"
import SecretsIcon from "@/images/icons/secrets.svg"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import TermLink from "@/components/TermLink"
import FactionLink from "../FactionLink"
import Faction from "@/classes/Faction"
import { useAuthContext } from "@/contexts/AuthContext"

interface NotificationProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// Notification for when a senator dies during the mortality phase
const NewSecretNotification = ({ notification }: NotificationProps) => {
  const { darkMode } = useAuthContext()
  const { allFactions } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction
    ? allFactions.byId[notification.faction] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={SecretsIcon} alt="secrets icon" width={30} height={30} />
    </div>
  )

  if (!faction) return null

  return (
    <Alert
      icon={getIcon()}
      style={{
        backgroundColor: darkMode
          ? faction.getColor(900)
          : faction.getColor(100),
        border: `solid 1px ${
          darkMode ? faction.getColor(950) : faction.getColor(300)
        }`,
      }}
    >
      <b>New Secret</b>
      <p>
        <FactionLink faction={faction} /> has gained a new{" "}
        <TermLink name="Secret" />.
      </p>
    </Alert>
  )
}

export default NewSecretNotification
