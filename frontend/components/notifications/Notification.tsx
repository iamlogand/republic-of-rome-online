import Notification from "@/classes/Notification"
import SelectFactionLeaderNotification from "./Notification_SelectFactionLeader"

interface NotificationItemProps {
  notification: Notification
}

// Container for a notification, which determines the type of notification to render
const NotificationContainer = (props: NotificationItemProps) => {

  // TODO some flow control to determine which type of notification to render
  return (
    <SelectFactionLeaderNotification notification={props.notification}/>
  )
}

export default NotificationContainer
