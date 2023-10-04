import { Alert } from "@mui/material"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faHourglass } from "@fortawesome/free-regular-svg-icons"
import ActionLog from "@/classes/ActionLog"
import styles from "./ActionLog.module.css"

interface NotificationProps {
  notification: ActionLog
}

// Notification for when a senator dies during the mortality phase
const NewTurnNotification = ({ notification }: NotificationProps) => {
  // Get notification-specific data
  const turnIndex = notification.data?.turn_index ?? null

  const getIcon = () => (
    <div className={`${styles.icon} ${styles.faIcon}`}>
      <FontAwesomeIcon icon={faHourglass} />
    </div>
  )

  return (
    <Alert
      icon={getIcon()}
      style={{ backgroundColor: "var(--background-color-neutral)" }}
    >
      <b>New Turn</b>
      <p>Turn {turnIndex} has started.</p>
    </Alert>
  )
}

export default NewTurnNotification
