import { ComponentType } from "react"

import { CustomActionFormProps } from "../../ActionDispatcher"
import AdvancedVoteForm from "../AdvancedVoteForm"
import AttemptPersuasionForm from "../AttemptPersuasionForm"
import ContinuePersuasionForm from "../ContinuePersuasionForm"
import CounterBribeForm from "../CounterBribeForm"
import RedistributeTalentsForm from "../RedistributeTalentsForm"

export const customActionFormRegistry: Record<
  string,
  ComponentType<CustomActionFormProps>
> = {
  "Advanced vote": AdvancedVoteForm,
  "Attempt persuasion": AttemptPersuasionForm,
  "Continue persuasion": ContinuePersuasionForm,
  "Counter-bribe": CounterBribeForm,
  "Redistribute talents": RedistributeTalentsForm,
}
