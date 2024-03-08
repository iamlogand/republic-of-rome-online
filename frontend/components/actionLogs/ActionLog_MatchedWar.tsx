import Image from "next/image"
import MilitaryIcon from "@/images/icons/military.svg"
import ActionLog from "@/classes/ActionLog"
import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import { capitalize } from "@mui/material/utils"
import ActionLogLayout from "@/components/ActionLogLayout"

interface NotificationProps {
  notification: ActionLog
}

// Notification for when an existing war is matched by another war or an enemy leader during the forum phase
const MatchedWarNotification = ({ notification }: NotificationProps) => {
  const { enemyLeaders, wars } = useGameContext()

  // Get notification-specific data
  const war: War | null = notification.data
    ? wars.byId[notification.data.war] ?? null
    : null
  const newStatus = notification.data ? notification.data.new_status : null
  const newWar: War | null = notification.data
    ? wars.byId[notification.data.new_war] ?? null
    : null
  const newEnemyLeader = notification.data
    ? enemyLeaders.byId[notification.data.new_enemy_leader] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={MilitaryIcon} alt="war icon" width={30} height={30} />
    </div>
  )

  if (!war) return null

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title={`Matched War is now ${capitalize(newStatus)}`}
    >
      <p>
        The {war.getName()} is has developed from Inactive to{" "}
        {capitalize(newStatus)} because it was Matched by{" "}
        {newWar ? (
          <span>the {newWar.getName()}</span>
        ) : (
          newEnemyLeader && newEnemyLeader.name
        )}
        .
      </p>
    </ActionLogLayout>
  )
}

export default MatchedWarNotification
