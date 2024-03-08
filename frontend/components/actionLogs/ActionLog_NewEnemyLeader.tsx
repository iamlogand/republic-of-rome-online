import Image from "next/image"
import MilitaryIcon from "@/images/icons/military.svg"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"
import Faction from "@/classes/Faction"
import EnemyLeaderDataCollection from "@/data/enemyLeaders.json"
import EnemyLeaderDataCollectionType from "@/types/EnemyLeader"
import FactionLink from "@/components/FactionLink"
import ActionLogLayout from "@/components/ActionLogLayout"

const typedEnemyLeaderDataCollection: EnemyLeaderDataCollectionType =
  EnemyLeaderDataCollection

interface NotificationProps {
  notification: ActionLog
}

// Notification for when a new enemy leader appears during the forum phase
const NewEnemyLeaderNotification = ({ notification }: NotificationProps) => {
  const { allFactions, enemyLeaders, wars } = useGameContext()

  // Get notification-specific data
  const enemyLeader: EnemyLeader | null = notification.data
    ? enemyLeaders.byId[notification.data.enemy_leader] ?? null
    : null
  const matching_war: War | null = notification.data
    ? wars.byId[notification.data.matching_war] ?? null
    : null
  const initiatingFaction: Faction | null = notification.data
    ? allFactions.byId[notification.data.initiating_faction] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={MilitaryIcon} alt="war icon" width={30} height={30} />
    </div>
  )

  if (!enemyLeader || !initiatingFaction) return null

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title="New Enemy Leader"
    >
      <p>
        In {typedEnemyLeaderDataCollection[enemyLeader.name]["location"]}, an
        Enemy Leader named {enemyLeader.name} has{" "}
        {typedEnemyLeaderDataCollection[enemyLeader.name]["new_description"]}.{" "}
        {matching_war ? (
          <span>
            His involvement with the {matching_war?.getName()} will make it
            harder to defeat
          </span>
        ) : (
          "He is idle for now"
        )}
        .{" "}
        <i>
          Situation initiated by <FactionLink faction={initiatingFaction} />
        </i>
        .
      </p>
    </ActionLogLayout>
  )
}

export default NewEnemyLeaderNotification
