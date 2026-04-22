import { ComponentType } from "react"

import { CustomActionFormProps } from "../../ActionDispatcher"
import AdvancedVoteForm from "../AdvancedVoteForm"
import AttemptAssassinationForm from "../AttemptAssassinationForm"
import AttemptPersuasionForm from "../AttemptPersuasionForm"
import ContinuePersuasionForm from "../ContinuePersuasionForm"
import CounterBribeForm from "../CounterBribeForm"
import PlaySecretBodyguardForm from "../PlaySecretBodyguardForm"
import ProposeDeployingForcesForm from "../ProposeDeployingForcesForm"
import ProposeReplacingProconsulForm from "../ProposeReplacingProconsulForm"
import RedistributeTalentsForm from "../RedistributeTalentsForm"

export const customActionFormRegistry: Record<
  string,
  ComponentType<CustomActionFormProps>
> = {
  "Advanced vote": AdvancedVoteForm,
  "Attempt assassination": AttemptAssassinationForm,
  "Attempt persuasion": AttemptPersuasionForm,
  "Continue persuasion": ContinuePersuasionForm,
  "Counter-bribe": CounterBribeForm,
  "Play secret bodyguard": PlaySecretBodyguardForm,
  "Propose deploying forces": ProposeDeployingForcesForm,
  "Propose replacing proconsul": ProposeReplacingProconsulForm,
  "Redistribute talents": RedistributeTalentsForm,
}
