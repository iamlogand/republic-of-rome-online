import Image from "next/image"
import { Alert } from "@mui/material"
import TimeIcon from "@/images/icons/time.svg"
import ActionLog from "@/classes/ActionLog"

interface NotificationProps {
  notification: ActionLog
}

// Notification for when a senator dies during the mortality phase
const NewTurnNotification = ({ notification }: NotificationProps) => {
  // Get notification-specific data
  const turnIndex = notification.data?.turn_index ?? null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={TimeIcon} alt="Time icon" width={30} height={30} />
    </div>
  )

  return (
    <Alert icon={getIcon()}>
      <b>New Turn</b>
      <p>Turn {turnIndex} has started.</p>
    </Alert>
  )
}

export default NewTurnNotification
