import Notification from "@/classes/Notification"
import SelectFactionLeaderNotification from "./Notification_SelectFactionLeader"
import styles from "./Notification.module.css"

interface NotificationItemProps {
  notification: Notification
}

// Container for a notification, which determines the type of notification to render
const NotificationContainer = (props: NotificationItemProps) => {

  // TODO some flow control to determine which type of notification to render
  return (
    <div className={styles.notificationItem}>
      <SelectFactionLeaderNotification notification={props.notification}/>
    </div>
  )
}

export default NotificationContainer
