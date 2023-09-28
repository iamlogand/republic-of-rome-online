import { Alert } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import styles from "./Notification.module.css"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from '@/components/FactionLink'

interface NotificationProps {
  notification: ActionLog
}

// Notification for when a new faction leader is selected
const SelectFactionLeaderNotification = ({ notification } : NotificationProps) => {
  const { allFactions, allSenators } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction ? allFactions.byId[notification.faction] ?? null : null
  const oldFactionLeader: Senator | null = notification.data ? allSenators.byId[notification.data.previous_senator] ?? null : null
  const newFactionLeader: Senator | null = notification.data ? allSenators.byId[notification.data.senator] ?? null : null

  const getIcon = () => {
    if (faction) {
      return (
        <div className={styles.icon}>
          <FactionIcon faction={faction} size={18} selectable />
        </div>
      )
    } else {
      return false
    }
  }

  if (faction && newFactionLeader) {
    return (
      <Alert icon={getIcon()} style={{backgroundColor: faction.getColor("textBg")}}>
        <b>New Faction Leader</b>
        <p>
          <SenatorLink senator={newFactionLeader} /> now holds the position of <FactionLink faction={faction} /> Leader
          {oldFactionLeader ? ', taking over from ' + <SenatorLink senator={oldFactionLeader} /> + '.' : '.'}
        </p>
      </Alert>
    )
    } else {
    return null
  }
}

export default SelectFactionLeaderNotification
