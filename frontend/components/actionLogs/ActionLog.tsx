import ActionLog from "@/classes/ActionLog"
import SelectFactionLeaderNotification from "./ActionLog_SelectFactionLeader"
import FaceMortalityNotification from "./ActionLog_FaceMortality"
import TemporaryRomeConsulNotification from "./ActionLog_TemporaryRomeConsul"
import NewTurnNotification from "./ActionLog_NewTurn"

interface NotificationItemProps {
  notification: ActionLog
  senatorDetails?: boolean
}

const notifications: { [key: string]: React.ComponentType<any> } = {
  select_faction_leader: SelectFactionLeaderNotification,
  face_mortality: FaceMortalityNotification,
  temporary_rome_consul: TemporaryRomeConsulNotification,
  new_turn: NewTurnNotification
}

// Container for a notification, which determines the type of notification to render
const NotificationContainer = (props: NotificationItemProps) => {
  const ContentComponent = notifications[props.notification.type]
  return (
    <ContentComponent notification={props.notification} senatorDetails={props.senatorDetails} />
  )
}

export default NotificationContainer
