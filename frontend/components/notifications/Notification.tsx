import ActionLog from "@/classes/ActionLog"
import SelectFactionLeaderNotification from "./Notification_SelectFactionLeader"
import FaceMortalityNotification from "./Notification_FaceMortality"
import TemporaryRomeConsulNotification from "./Notification_TemporaryRomeConsul"

interface NotificationItemProps {
  notification: ActionLog
}

const notifications: { [key: string]: React.ComponentType<any> } = {
  select_faction_leader: SelectFactionLeaderNotification,
  face_mortality: FaceMortalityNotification,
  temporary_rome_consul: TemporaryRomeConsulNotification
}

// Container for a notification, which determines the type of notification to render
const NotificationContainer = (props: NotificationItemProps) => {
  const ContentComponent = notifications[props.notification.type]
  return (
    <ContentComponent notification={props.notification}/>
  )
}

export default NotificationContainer
