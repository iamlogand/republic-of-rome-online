import { Alert } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import styles from "./ActionLog.module.css"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "@/components/FactionLink"

interface NotificationProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// Notification for when a new faction leader is selected
const SelectFactionLeaderNotification = ({
  notification,
  senatorDetails,
}: NotificationProps) => {
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
      <div className={styles.icon}>
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
    <Alert
      icon={getIcon()}
      style={{ backgroundColor: faction.getColor(100), border: `solid 1px ${faction.getColor(300)}` }}
    >
      <b>New Faction Leader</b>
      {getText()}
    </Alert>
  )
}

export default SelectFactionLeaderNotification
