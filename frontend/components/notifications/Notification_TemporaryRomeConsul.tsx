import { Alert } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from '@/components/FactionLink'
import Faction from "@/classes/Faction"
import Senator from '@/classes/Senator'
import { useGameContext } from "@/contexts/GameContext"
import styles from "./Notification.module.css"
import FactionIcon from "@/components/FactionIcon"

interface NotificationProps {
  notification: ActionLog
}

const TemporaryRomeConsulNotification = ({ notification } : NotificationProps) => {
  const { allFactions, allSenators } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction ? allFactions.byId[notification.faction] ?? null : null
  const senator: Senator | null = notification.data.senator ? allSenators.byId[notification.data.senator] ?? null : null

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

  if (!faction || !senator) return null

  return (
    <Alert icon={getIcon()} style={{backgroundColor: faction.getColor("textBg")}}>
      <b>Temporary Rome Consul</b>
      <p>
        <SenatorLink senator={senator} /> of the <FactionLink faction={faction} /> now serves as our Temporary Rome Consul, making him the HRAO.
      </p>
    </Alert>
  )
}

export default TemporaryRomeConsulNotification
