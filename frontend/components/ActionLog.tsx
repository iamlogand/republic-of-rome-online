import ActionLog from "@/classes/ActionLog"
import NewFactionLeaderActionLog from "@/components/actionLogs/NewFactionLeaderActionLog"
import MortalityActionLog from "@/components/actionLogs/MortalityActionLog"
import TemporaryRomeConsulActionLog from "@/components/actionLogs/TemporaryRomeConsulActionLog"
import NewFamilyActionLog from "@/components/actionLogs/NewFamilyActionLog"
import NewWarActionLog from "@/components/actionLogs/NewWarActionLog"
import MatchedWarActionLog from "@/components/actionLogs/MatchedWarActionLog"
import NewEnemyLeaderActionLog from "@/components/actionLogs/NewEnemyLeaderActionLog"
import MatchedEnemyLeaderActionLog from "@/components/actionLogs/MatchedEnemyLeaderActionLog"
import NewSecretActionLog from "@/components/actionLogs/NewSecretActionLog"
import PersonalRevenueActionLog from "@/components/actionLogs/PersonalRevenueActionLog"
import EraEndsActionLog from "@/components/actionLogs/EraEndsActionLog"
import FactionWinsActionLog from "@/components/actionLogs/FactionWinsActionLog"
import NewConcessionActionLog from "@/components/actionLogs/NewConcessionActionLog"

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
  new_concession: NewConcessionActionLog,
  new_enemy_leader: NewEnemyLeaderActionLog,
  new_family: NewFamilyActionLog,
  new_secret: NewSecretActionLog,
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
