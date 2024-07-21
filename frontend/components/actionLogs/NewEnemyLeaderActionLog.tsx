import Image from "next/image"
import EnemyLeaderIcon from "@/images/icons/enemyLeader.svg"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"
import Faction from "@/classes/Faction"
import EnemyLeaderDataCollection from "@/data/enemyLeaders.json"
import EnemyLeaderDataCollectionType from "@/types/EnemyLeader"
import FactionLink from "@/components/FactionLink"
import ActionLogLayout from "@/components/ActionLogLayout"
import TermLink from "@/components/TermLink"
import FormattedWarName from "../FormattedWarName"

const typedEnemyLeaderDataCollection: EnemyLeaderDataCollectionType =
  EnemyLeaderDataCollection

interface ActionLogProps {
  notification: ActionLog
}

// ActionLog for when a new enemy leader appears during the forum phase
const NewEnemyLeaderActionLog = ({ notification }: ActionLogProps) => {
  const { allFactions, enemyLeaders, wars } = useGameContext()

  // Get notification-specific data
  const enemyLeader: EnemyLeader | null = notification.data
    ? enemyLeaders.byId[notification.data.enemy_leader] ?? null
    : null
  const matchingWar: War | null = notification.data
    ? wars.byId[notification.data.matching_war] ?? null
    : null
  const initiatingFaction: Faction | null = notification.data
    ? allFactions.byId[notification.data.initiating_faction] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={EnemyLeaderIcon} alt="War icon" width={30} height={30} />
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
        In {typedEnemyLeaderDataCollection[enemyLeader.name]["location"]}, an{" "}
        <TermLink name="Enemy Leader" /> named {enemyLeader.name} has{" "}
        {typedEnemyLeaderDataCollection[enemyLeader.name]["new_description"]}.{" "}
        {matchingWar ? (
          <span>
            His involvement with the <FormattedWarName war={matchingWar} /> will
            make it harder to defeat
          </span>
        ) : (
          "He is idle for now"
        )}
        .{" "}
        <i>
          Initiated by <FactionLink faction={initiatingFaction} />
        </i>
        .
      </p>
    </ActionLogLayout>
  )
}

export default NewEnemyLeaderActionLog
