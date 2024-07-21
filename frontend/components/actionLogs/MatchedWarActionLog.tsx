import Image from "next/image"
import WarIcon from "@/images/icons/war.svg"
import ActionLog from "@/classes/ActionLog"
import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import { capitalize } from "@mui/material/utils"
import ActionLogLayout from "@/components/ActionLogLayout"
import TermLink from "@/components/TermLink"
import FormattedWarName from "@/components/FormattedWarName"

interface ActionLogProps {
  notification: ActionLog
}

// ActionLog for when an existing war is matched by another war or an enemy leader during the forum phase
const MatchedWarActionLog = ({ notification }: ActionLogProps) => {
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
      <Image src={WarIcon} alt="War icon" width={30} height={30} />
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
        The <FormattedWarName war={war} /> has developed from{" "}
        <TermLink name="Inactive War" displayName="Inactive" /> to {}
        <TermLink
          name={`${capitalize(newStatus)} War`}
          displayName={capitalize(newStatus)}
        />{" "}
        because it was{" "}
        <TermLink
          name="Matching Wars and Enemy Leaders"
          displayName="Matched"
        />{" "}
        by{" "}
        {newWar ? (
          <span>
            the <FormattedWarName war={newWar} />
          </span>
        ) : (
          newEnemyLeader && newEnemyLeader.name
        )}
        .
      </p>
    </ActionLogLayout>
  )
}

export default MatchedWarActionLog
