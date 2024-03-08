import Image from "next/image"
import TimeIcon from "@/images/icons/time.svg"
import ActionLog from "@/classes/ActionLog"
import ActionLogLayout from "@/components/ActionLogLayout"

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
    <ActionLogLayout actionLog={notification} icon={getIcon()} title="New Turn">
      <p>Turn {turnIndex} has started.</p>
    </ActionLogLayout>
  )
}

export default NewTurnNotification
