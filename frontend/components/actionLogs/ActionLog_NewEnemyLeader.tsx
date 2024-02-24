import Image from "next/image"
import { Alert } from "@mui/material"
import MilitaryIcon from "@/images/icons/military.svg"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"
import Faction from "@/classes/Faction"
import EnemyLeaderDataCollection from "@/data/enemyLeaders.json"
import EnemyLeaderDataCollectionType from "@/types/EnemyLeader"
import FactionLink from "@/components/FactionLink"

const typedEnemyLeaderDataCollection: EnemyLeaderDataCollectionType =
  EnemyLeaderDataCollection

interface NotificationProps {
  notification: ActionLog
}

// Notification for when a new war appears during the forum phase
const NewEnemyLeaderNotification = ({ notification }: NotificationProps) => {
  const { allFactions, enemyLeaders, wars } = useGameContext()

  // Get notification-specific data
  const enemyLeader: EnemyLeader | null = notification.data
    ? enemyLeaders.byId[notification.data.enemy_leader] ?? null
    : null
  const matching_war: War | null = notification.data
    ? wars.byId[notification.data.matching_war] ?? null
    : null
  const activatedTheWar: boolean = notification.data
    ? notification.data.activated_the_war
    : false
  const initiatingFaction: Faction | null = notification.data
    ? allFactions.byId[notification.data.initiating_faction] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={MilitaryIcon} alt="War Icon" width={30} height={30} />
    </div>
  )

  if (!enemyLeader || !initiatingFaction) return null

  return (
    <Alert icon={getIcon()}>
      <b>New Enemy Leader</b>
      <p>
        In {typedEnemyLeaderDataCollection[enemyLeader.name]["location"]}, a
        talented commander named {enemyLeader.name} has{" "}
        {typedEnemyLeaderDataCollection[enemyLeader.name]["new_description"]}.{" "}
        <i>
          Situation initiated by <FactionLink faction={initiatingFaction} />
        </i>
        .
      </p>
    </Alert>
  )
}

export default NewEnemyLeaderNotification
