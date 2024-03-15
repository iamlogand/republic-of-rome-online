import ActionLog from "@/classes/ActionLog"
import SelectFactionLeaderActionLog from "./actionLogs/ActionLog_SelectFactionLeader"
import FaceMortalityActionLog from "./actionLogs/ActionLog_FaceMortality"
import TemporaryRomeConsulActionLog from "./actionLogs/ActionLog_TemporaryRomeConsul"
import NewTurnActionLog from "./actionLogs/ActionLog_NewTurn"
import NewFamilyActionLog from "./actionLogs/ActionLog_NewFamily"
import NewWarActionLog from "./actionLogs/ActionLog_NewWar"
import MatchedWarActionLog from "./actionLogs/ActionLog_MatchedWar"
import NewEnemyLeaderActionLog from "./actionLogs/ActionLog_NewEnemyLeader"
import MatchedEnemyLeaderActionLog from "./actionLogs/ActionLog_MatchedEnemyLeader"
import NewSecretActionLog from "./actionLogs/ActionLog_NewSecret"

interface ActionLogItemProps {
  notification: ActionLog
  senatorDetails?: boolean
}

const notifications: { [key: string]: React.ComponentType<any> } = {
  face_mortality: FaceMortalityActionLog,
  matched_enemy_leader: MatchedEnemyLeaderActionLog,
  matched_war: MatchedWarActionLog,
  new_enemy_leader: NewEnemyLeaderActionLog,
  new_family: NewFamilyActionLog,
  new_secret: NewSecretActionLog,
  new_turn: NewTurnActionLog,
  new_war: NewWarActionLog,
  select_faction_leader: SelectFactionLeaderActionLog,
  temporary_rome_consul: TemporaryRomeConsulActionLog,
}

// Container for a notification, which determines the type of notification to render
const ActionLogContainer = (props: ActionLogItemProps) => {
  const ContentComponent = notifications[props.notification.type]
  return (
    <ContentComponent
      notification={props.notification}
      senatorDetails={props.senatorDetails}
    />
  )
}

export default ActionLogContainer
