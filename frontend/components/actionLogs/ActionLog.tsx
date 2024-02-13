import ActionLog from "@/classes/ActionLog"
import SelectFactionLeaderNotification from "./ActionLog_SelectFactionLeader"
import FaceMortalityNotification from "./ActionLog_FaceMortality"
import TemporaryRomeConsulNotification from "./ActionLog_TemporaryRomeConsul"
import NewTurnNotification from "./ActionLog_NewTurn"
import NewFamilyNotification from "./ActionLog_NewFamily"
import NewWarNotification from "./ActionLog_NewWar"
import MatchedWarNotification from "./ActionLog_MatchedWar"
import NewEnemyLeaderNotification from "./ActionLog_NewEnemyLeader"

interface NotificationItemProps {
  notification: ActionLog
  senatorDetails?: boolean
}

const notifications: { [key: string]: React.ComponentType<any> } = {
  face_mortality: FaceMortalityNotification,
  matched_war: MatchedWarNotification,
  new_family: NewFamilyNotification,
  new_turn: NewTurnNotification,
  new_war: NewWarNotification,
  select_faction_leader: SelectFactionLeaderNotification,
  temporary_rome_consul: TemporaryRomeConsulNotification,
  new_enemy_leader: NewEnemyLeaderNotification,
}

// Container for a notification, which determines the type of notification to render
const NotificationContainer = (props: NotificationItemProps) => {
  const ContentComponent = notifications[props.notification.type]
  return (
    <ContentComponent
      notification={props.notification}
      senatorDetails={props.senatorDetails}
    />
  )
}

export default NotificationContainer
