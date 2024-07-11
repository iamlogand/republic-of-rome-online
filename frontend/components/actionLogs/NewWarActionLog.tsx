import Image from "next/image"
import WarIcon from "@/images/icons/war.svg"
import ActionLog from "@/classes/ActionLog"
import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import FactionLink from "@/components/FactionLink"
import Faction from "@/classes/Faction"
import { capitalize } from "@mui/material/utils"
import EnemyLeader from "@/classes/EnemyLeader"
import ActionLogLayout from "@/components/ActionLogLayout"
import TermLink from "@/components/TermLink"
import FormattedWarName from "../FormattedWarName"

interface ActionLogProps {
  notification: ActionLog
}

// ActionLog for when a new war appears during the forum phase
const NewWarActionLog = ({ notification }: ActionLogProps) => {
  const { allFactions, wars, enemyLeaders } = useGameContext()

  // Get notification-specific data
  const newWar: War | null = notification.data
    ? wars.byId[notification.data.war] ?? null
    : null
  const initialStatus = notification.data
    ? notification.data.initial_status
    : null
  const initiatingFaction: Faction | null = notification.data
    ? allFactions.byId[notification.data.initiating_faction] ?? null
    : null
  const matchingWarIds = notification.data
    ? notification.data.matching_wars ?? []
    : []
  const isMatchedByMultiple = matchingWarIds.length > 1

  // These are any enemy leader(s) that were idle but have matched and activated this war
  const activatingEnemyLeaders: EnemyLeader[] = notification.data
    .activating_enemy_leaders
    ? enemyLeaders.asArray.filter((leader) =>
        notification.data.activating_enemy_leaders.includes(leader.id)
      )
    : []

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={WarIcon} alt="War Icon" width={30} height={30} />
    </div>
  )

  const getStatusAndExplanation = () => {
    switch (initialStatus) {
      case "imminent":
        return (
          <span>
            Imminent due to {isMatchedByMultiple ? "" : "a "}
            <TermLink
              name="Matching Wars and Enemy Leaders"
              displayName="Matching War"
              plural={isMatchedByMultiple}
            />
          </span>
        )
      case "active":
        return activatingEnemyLeaders.length == 0 ? (
          <span>
            inherently <TermLink name="Active War" displayName="Active" />
          </span>
        ) : (
          <span>
            Active due to{" "}
            {activatingEnemyLeaders.length == 1 ? (
              <span>
                a Matching Enemy Leader: {activatingEnemyLeaders[0].name}
              </span>
            ) : (
              <span>
                Matching Enemy Leaders: {activatingEnemyLeaders[0].name} and{" "}
                {activatingEnemyLeaders[1].name}
              </span>
            )}
          </span>
        )
      default:
        return (
          <TermLink
            name={`${capitalize(initialStatus)} War`}
            displayName={capitalize(initialStatus)}
          />
        )
    }
  }

  if (!newWar || !initiatingFaction) return null

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title={`New ${capitalize(initialStatus)} War`}
    >
      <p>
        Rome faces a new threat in the <FormattedWarName war={newWar} />. This{" "}
        <TermLink name="War" /> is {getStatusAndExplanation()}.{" "}
        <i>
          Initiated by <FactionLink faction={initiatingFaction} />
        </i>
        .
      </p>
    </ActionLogLayout>
  )
}

export default NewWarActionLog
