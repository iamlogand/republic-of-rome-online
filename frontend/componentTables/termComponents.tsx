import PriorConsulTerm from "@/components/terms/PriorConsulTerm"
import FactionTerm from "@/components/terms/FactionTerm"
import SecretTerm from "@/components/terms/SecretTerm"
import SenatorTerm from "@/components/terms/SenatorTerm"
import MortalityPhaseTerm from "@/components/terms/MortalityPhaseTerm"
import ForumPhaseTerm from "@/components/terms/ForumPhaseTerm"
import RevolutionPhaseTerm from "@/components/terms/RevolutionPhaseTerm"
import CombatPhaseTerm from "@/components/terms/CombatPhaseTerm"
import PopulationPhaseTerm from "@/components/terms/PopulationPhaseTerm"
import RevenuePhaseTerm from "@/components/terms/RevenuePhaseTerm"
import SenatePhaseTerm from "@/components/terms/SenatePhaseTerm"
import TurnTerm from "@/components/terms/TurnTerm"
import FactionPhaseTerm from "@/components/terms/FactionPhaseTerm"
import FinalForumPhaseTerm from "@/components/terms/FinalForumPhaseTerm"
import RomeConsulTerm from "@/components/terms/RomeConsulTerm"
import HraoTerm from "@/components/terms/HraoTerm"
import WarTerm from "@/components/terms/WarTerm"
import ActiveWarTerm from "@/components/terms/ActiveWarTerm"
import FactionLeaderTerm from "@/components/terms/FactionLeaderTerm"
import AlignedSenatorTerm from "@/components/terms/AlignedSenatorTerm"
import UnalignedSenatorTerm from "@/components/terms/UnalignedSenatorTerm"
import FamilyTerm from "@/components/terms/FamilyTerm"
import StatesmanTerm from "@/components/terms/StatesmanTerm"
import ImminentWarTerm from "@/components/terms/ImminentWarTerm"
import InactiveWarTerm from "@/components/terms/InactiveWarTerm"
import EnemyLeaderTerm from "@/components/terms/EnemyLeaderTerm"
import MatchingWarsAndEnemyLeadersTerm from "@/components/terms/MatchingWarsAndEnemyLeadersTerm"
import MilitaryTerm from "@/components/terms/MilitaryTerm"
import OratoryTerm from "@/components/terms/OratoryTerm"
import LoyaltyTerm from "@/components/terms/LoyaltyTerm"
import InfluenceTerm from "@/components/terms/InfluenceTerm"
import PersonalTreasuryTerm from "@/components/terms/PersonalTreasuryTerm"
import PopularityTerm from "@/components/terms/PopularityTerm"
import VotesTerm from "@/components/terms/VotesTerm"
import KnightsTerm from "@/components/terms/KnightsTerm"
import TalentTerm from "@/components/terms/TalentsTerm"

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
  Knights: <KnightsTerm />,
  Loyalty: <LoyaltyTerm />,
  "Matching Wars and Enemy Leaders": <MatchingWarsAndEnemyLeadersTerm />,
  Military: <MilitaryTerm />,
  "Mortality Phase": <MortalityPhaseTerm />,
  Oratory: <OratoryTerm />,
  "Personal Treasury": <PersonalTreasuryTerm />,
  Popularity: <PopularityTerm />,
  "Population Phase": <PopulationPhaseTerm />,
  "Prior Consul": <PriorConsulTerm />,
  "Revenue Phase": <RevenuePhaseTerm />,
  "Revolution Phase": <RevolutionPhaseTerm />,
  "Rome Consul": <RomeConsulTerm />,
  Secret: <SecretTerm />,
  "Senate Phase": <SenatePhaseTerm />,
  Senator: <SenatorTerm />,
  Statesman: <StatesmanTerm />,
  Talent: <TalentTerm />,
  "Temporary Rome Consul": <RomeConsulTerm />,
  Turn: <TurnTerm />,
  "Unaligned Senator": <UnalignedSenatorTerm />,
  Votes: <VotesTerm />,
  War: <WarTerm />,
}

export default termComponents
