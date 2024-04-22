import ActionLog from "@/classes/ActionLog"
import NewFactionLeaderActionLog from "@/components/actionLogs/ActionLog_NewFactionLeader"
import MortalityActionLog from "@/components/actionLogs/ActionLog_Mortality"
import TemporaryRomeConsulActionLog from "@/components/actionLogs/ActionLog_TemporaryRomeConsul"
import NewTurnActionLog from "@/components/actionLogs/ActionLog_NewTurn"
import NewFamilyActionLog from "@/components/actionLogs/ActionLog_NewFamily"
import NewWarActionLog from "@/components/actionLogs/ActionLog_NewWar"
import MatchedWarActionLog from "@/components/actionLogs/ActionLog_MatchedWar"
import NewEnemyLeaderActionLog from "@/components/actionLogs/ActionLog_NewEnemyLeader"
import MatchedEnemyLeaderActionLog from "@/components/actionLogs/ActionLog_MatchedEnemyLeader"
import NewSecretActionLog from "@/components/actionLogs/ActionLog_NewSecret"
import PersonalRevenueActionLog from "@/components/actionLogs/ActionLog_PersonalRevenue"
import EraEndsActionLog from "@/components/actionLogs/ActionLog_EraEnds"
import FactionWinsActionLog from "@/components/actionLogs/ActionLog_FactionWins"

interface ActionLogItemProps {
  notification: ActionLog
  senatorDetails?: boolean
}

const notifications: { [key: string]: React.ComponentType<any> } = {
  era_ends: EraEndsActionLog,
  faction_wins: FactionWinsActionLog,
  mortality: MortalityActionLog,
  matched_enemy_leader: MatchedEnemyLeaderActionLog,
  matched_war: MatchedWarActionLog,
  new_enemy_leader: NewEnemyLeaderActionLog,
  new_family: NewFamilyActionLog,
  new_secret: NewSecretActionLog,
  new_turn: NewTurnActionLog,
  new_war: NewWarActionLog,
  personal_revenue: PersonalRevenueActionLog,
  new_faction_leader: NewFactionLeaderActionLog,
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
