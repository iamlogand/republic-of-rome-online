import ActionLog from "@/classes/ActionLog"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "@/components/FactionLink"
import { useCookieContext } from "@/contexts/CookieContext"
import ActionLogLayout from "@/components/ActionLogLayout"

interface ActionLogProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// ActionLog for when a new faction leader is selected
const SelectFactionLeaderActionLog = ({
  notification,
  senatorDetails,
}: ActionLogProps) => {
  const { allFactions, allSenators } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction
    ? allFactions.byId[notification.faction] ?? null
    : null
  const oldFactionLeader: Senator | null = notification.data
    ? allSenators.byId[notification.data.previous_senator] ?? null
    : null
  const newFactionLeader: Senator | null = notification.data
    ? allSenators.byId[notification.data.senator] ?? null
    : null

  const getIcon = () => {
    if (!faction) return null
    return (
      <div className="h-[18px] w-[24px] flex justify-center">
        <FactionIcon faction={faction} size={22} selectable />
      </div>
    )
  }

  // Get the text for the notification (tense sensitive)
  const getText = () => {
    if (!newFactionLeader || !faction) return null

    return (
      <p>
        <SenatorLink senator={newFactionLeader} />{" "}
        {senatorDetails ? "became" : "now holds the position of"}{" "}
        <FactionLink faction={faction} /> Leader
        {oldFactionLeader && (
          <span>
            , taking over from <SenatorLink senator={oldFactionLeader} />
          </span>
        )}
        .
      </p>
    )
  }

  if (!newFactionLeader || !faction) return null

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title="New Faction Leader"
      faction={faction}
    >
      {getText()}
    </ActionLogLayout>
  )
}

export default SelectFactionLeaderActionLog
