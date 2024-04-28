import PriorConsulTerm from "@/components/terms/Term_PriorConsul"
import FactionTerm from "@/components/terms/Term_Faction"
import SecretTerm from "@/components/terms/Term_Secret"
import SenatorTerm from "@/components/terms/Term_Senator"
import MortalityPhaseTerm from "@/components/terms/Term_MortalityPhase"
import ForumPhaseTerm from "@/components/terms/Term_ForumPhase"
import RevolutionPhaseTerm from "@/components/terms/Term_RevolutionPhase"
import CombatPhaseTerm from "@/components/terms/Term_CombatPhase"
import PopulationPhaseTerm from "@/components/terms/Term_PopulationPhase"
import RevenuePhaseTerm from "@/components/terms/Term_RevenuePhase"
import SenatePhaseTerm from "@/components/terms/Term_SenatePhase"
import TurnTerm from "@/components/terms/Term_Turn"
import FactionPhaseTerm from "@/components/terms/Term_FactionPhase"
import FinalForumPhaseTerm from "@/components/terms/Term_FinalForumPhase"
import RomeConsulTerm from "@/components/terms/Term_RomeConsul"
import HraoTerm from "@/components/terms/Term_Hrao"
import WarTerm from "@/components/terms/Term_War"
import ActiveWarTerm from "@/components/terms/Term_ActiveWar"
import FactionLeaderTerm from "@/components/terms/Term_FactionLeader"
import AlignedSenatorTerm from "@/components/terms/Term_AlignedSenator"
import UnalignedSenatorTerm from "@/components/terms/Term_UnalignedSenator"
import FamilyTerm from "@/components/terms/Term_Family"
import StatesmanTerm from "@/components/terms/Term_Statesman"
import ImminentWarTerm from "@/components/terms/Term_ImminentWar"
import InactiveWarTerm from "@/components/terms/Term_InactiveWar"
import EnemyLeaderTerm from "@/components/terms/Term_EnemyLeader"
import MatchingWarsAndEnemyLeadersTerm from "@/components/terms/Term_MatchingWarsAndEnemyLeadersTerm"
import MilitaryTerm from "@/components/terms/Term_Military"
import OratoryTerm from "@/components/terms/Term_Oratory"
import LoyaltyTerm from "@/components/terms/Term_Loyalty"
import InfluenceTerm from "@/components/terms/Term_Influence"

interface TermComponents {
  [key: string]: JSX.Element
}

const termComponents: TermComponents = {
  "Active War": <ActiveWarTerm />,
  "Aligned Senator": <AlignedSenatorTerm />,
  "Combat Phase": <CombatPhaseTerm />,
  "Enemy Leader": <EnemyLeaderTerm />,
  Faction: <FactionTerm />,
  "Faction Leader": <FactionLeaderTerm />,
  "Faction Phase": <FactionPhaseTerm />,
  Family: <FamilyTerm />,
  "Final Forum Phase": <FinalForumPhaseTerm />,
  "Forum Phase": <ForumPhaseTerm />,
  HRAO: <HraoTerm />,
  "Imminent War": <ImminentWarTerm />,
  "Inactive War": <InactiveWarTerm />,
  Influence: <InfluenceTerm />,
  Loyalty: <LoyaltyTerm />,
  "Matching Wars and Enemy Leaders": <MatchingWarsAndEnemyLeadersTerm />,
  Military: <MilitaryTerm />,
  "Mortality Phase": <MortalityPhaseTerm />,
  Oratory: <OratoryTerm />,
  "Population Phase": <PopulationPhaseTerm />,
  "Prior Consul": <PriorConsulTerm />,
  "Revenue Phase": <RevenuePhaseTerm />,
  "Revolution Phase": <RevolutionPhaseTerm />,
  "Rome Consul": <RomeConsulTerm />,
  Secret: <SecretTerm />,
  "Senate Phase": <SenatePhaseTerm />,
  Senator: <SenatorTerm />,
  Statesman: <StatesmanTerm />,
  Turn: <TurnTerm />,
  "Unaligned Senator": <UnalignedSenatorTerm />,
  War: <WarTerm />,
}

export default termComponents
