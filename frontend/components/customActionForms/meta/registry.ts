import { ComponentType } from "react"

import { CustomActionFormProps } from "../../ActionDispatcher"
import RedistributeTalentsForm from "../RedistributeTalentsForm"

export const customActionFormRegistry: Record<
  string,
  ComponentType<CustomActionFormProps>
> = {
  "Redistribute talents": RedistributeTalentsForm,
}
