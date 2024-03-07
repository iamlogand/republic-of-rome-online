import ActionLog from "@/classes/ActionLog"
import SelectFactionLeaderNotification from "./actionLogs/ActionLog_SelectFactionLeader"
import FaceMortalityNotification from "./actionLogs/ActionLog_FaceMortality"
import TemporaryRomeConsulNotification from "./actionLogs/ActionLog_TemporaryRomeConsul"
import NewTurnNotification from "./actionLogs/ActionLog_NewTurn"
import NewFamilyNotification from "./actionLogs/ActionLog_NewFamily"
import NewWarNotification from "./actionLogs/ActionLog_NewWar"
import MatchedWarNotification from "./actionLogs/ActionLog_MatchedWar"
import NewEnemyLeaderNotification from "./actionLogs/ActionLog_NewEnemyLeader"
import MatchedEnemyLeaderNotification from "./actionLogs/ActionLog_MatchedEnemyLeader"
import NewSecretNotification from "./actionLogs/ActionLog_NewSecret"

interface NotificationItemProps {
  notification: ActionLog
  senatorDetails?: boolean
}

const notifications: { [key: string]: React.ComponentType<any> } = {
  face_mortality: FaceMortalityNotification,
  matched_enemy_leader: MatchedEnemyLeaderNotification,
  matched_war: MatchedWarNotification,
  new_enemy_leader: NewEnemyLeaderNotification,
  new_family: NewFamilyNotification,
  new_secret: NewSecretNotification,
  new_turn: NewTurnNotification,
  new_war: NewWarNotification,
  select_faction_leader: SelectFactionLeaderNotification,
  temporary_rome_consul: TemporaryRomeConsulNotification,
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
