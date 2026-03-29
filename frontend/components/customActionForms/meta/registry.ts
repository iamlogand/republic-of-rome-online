import { ComponentType } from "react"

import { CustomActionFormProps } from "../../ActionDispatcher"
import AdvancedVoteForm from "../AdvancedVoteForm"
import RedistributeTalentsForm from "../RedistributeTalentsForm"

export const customActionFormRegistry: Record<
  string,
  ComponentType<CustomActionFormProps>
> = {
  "Advanced vote": AdvancedVoteForm,
  "Redistribute talents": RedistributeTalentsForm,
}
