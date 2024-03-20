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

interface TermComponents {
  [key: string]: JSX.Element
}

const termComponents: TermComponents = {
  "Combat Phase": <CombatPhaseTerm />,
  Faction: <FactionTerm />,
  "Faction Phase": <FactionPhaseTerm />,
  "Final Forum Phase": <FinalForumPhaseTerm />,
  "Forum Phase": <ForumPhaseTerm />,
  HRAO: <HraoTerm />,
  "Mortality Phase": <MortalityPhaseTerm />,
  "Population Phase": <PopulationPhaseTerm />,
  "Prior Consul": <PriorConsulTerm />,
  "Revenue Phase": <RevenuePhaseTerm />,
  "Revolution Phase": <RevolutionPhaseTerm />,
  "Rome Consul": <RomeConsulTerm />,
  Secret: <SecretTerm />,
  "Senate Phase": <SenatePhaseTerm />,
  Senator: <SenatorTerm />,
  Turn: <TurnTerm />,
}

export default termComponents
