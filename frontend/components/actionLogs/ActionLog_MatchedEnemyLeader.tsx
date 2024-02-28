import Image from "next/image"
import { Alert } from "@mui/material"
import MilitaryIcon from "@/images/icons/military.svg"
import ActionLog from "@/classes/ActionLog"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"
import { useGameContext } from "@/contexts/GameContext"

interface NotificationProps {
  notification: ActionLog
}

// Notification for when an existing enemy leader is matched by a war during the forum phase
const MatchedEnemyLeaderNotification = ({
  notification,
}: NotificationProps) => {
  const { wars, enemyLeaders } = useGameContext()

  // Get notification-specific data
  const enemyLeader: EnemyLeader | null = notification.data
    ? enemyLeaders.byId[notification.data.enemy_leader] ?? null
    : null
  const newWar: War | null = notification.data
    ? wars.byId[notification.data.new_war] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={MilitaryIcon} alt="War Icon" width={30} height={30} />
    </div>
  )

  if (!enemyLeader || !newWar) return null

  return (
    <Alert icon={getIcon()}>
      <b>New War Matches Enemy Leader</b>
      <p>
        The {newWar.getName()} is a Matching War for {enemyLeader.name}. His
        involvement will make it harder to defeat.
      </p>
    </Alert>
  )
}

export default MatchedEnemyLeaderNotification
