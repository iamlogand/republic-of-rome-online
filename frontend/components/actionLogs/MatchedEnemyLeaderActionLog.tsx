import Image from "next/image"
import EnemyLeaderIcon from "@/images/icons/enemyLeader.svg"
import ActionLog from "@/classes/ActionLog"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"
import { useGameContext } from "@/contexts/GameContext"
import ActionLogLayout from "@/components/ActionLogLayout"
import TermLink from "@/components/TermLink"
import FormattedWarName from "@/components/FormattedWarName"

interface ActionLogProps {
  notification: ActionLog
}

// ActionLog for when an existing enemy leader is matched by a war during the forum phase
const MatchedEnemyLeaderActionLog = ({ notification }: ActionLogProps) => {
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
      <Image src={EnemyLeaderIcon} alt="War icon" width={30} height={30} />
    </div>
  )

  if (!enemyLeader || !newWar) return null

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title="New War Matches Enemy Leader"
    >
      <p>
        The <FormattedWarName war={newWar} /> is a{" "}
        <TermLink
          name="Matching Wars and Enemy Leaders"
          displayName="Matching War"
        />{" "}
        for {enemyLeader.name}. His involvement will make it harder to defeat.
      </p>
    </ActionLogLayout>
  )
}

export default MatchedEnemyLeaderActionLog
