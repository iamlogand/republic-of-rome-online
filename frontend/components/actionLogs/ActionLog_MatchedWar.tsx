import Image from "next/image"
import { Alert } from "@mui/material"
import MilitaryIcon from "@/images/icons/military.svg"
import ActionLog from "@/classes/ActionLog"
import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import { capitalize } from "@mui/material/utils"

interface NotificationProps {
  notification: ActionLog
}

// Notification for when an existing war is matched by another war or an enemy leader during the forum phase
const MatchedWarNotification = ({ notification }: NotificationProps) => {
  const { wars } = useGameContext()

  // Get notification-specific data
  const war: War | null = notification.data
    ? wars.byId[notification.data.war] ?? null
    : null
  const newStatus = notification.data ? notification.data.new_status : null
  const newWar: War | null = notification.data
    ? wars.byId[notification.data.new_war] ?? null
    : null

  // TODO: make this handle a new leader as well

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={MilitaryIcon} alt="War Icon" width={30} height={30} />
    </div>
  )

  if (!war || !newWar) return null

  return (
    <Alert icon={getIcon()}>
      <b>Matched War is now {capitalize(newStatus)}</b>
      <p>
        The {war.getName()} is has developed from Inactive to {capitalize(newStatus)} because it was Matched by the {newWar.getName()}.
      </p>
    </Alert>
  )
}

export default MatchedWarNotification
