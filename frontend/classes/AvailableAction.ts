export interface ActionSignals {
  [key: string]: string
}

export interface ActionCondition {
  value1: string | number
  operation: "==" | "!=" | ">=" | ">" | "<=" | "<"
  value2: string | number
}

export interface SelectOption {
  value: string
  name?: string
  object_class?: string
  id?: number
  signals?: ActionSignals
  conditions?: ActionCondition[]
}

export interface SelectField {
  type: "select"
  name: string
  options: SelectOption[]
  signals?: ActionSignals
  inline?: boolean
}

export interface MultiSelectField {
  type: "multiselect"
  name: string
  options: SelectOption[]
  signals?: ActionSignals
  inline?: boolean
}

export interface NumberField {
  type: "number"
  name: string
  min: (number | string)[]
  max: (number | string)[]
  signals?: ActionSignals
  inline?: boolean
}

export interface CalculationField {
  type: "calculation"
  name: string
  value: string
  label?: string
  conditions?: ActionCondition[]
  inline?: boolean
  style?: "warning"
}

export interface ChanceField {
  type: "chance"
  name: string
  dice: 1 | 2 | 3
  label?: string
  target_min?: number
  target_max?: number
  target_exacts?: (number | string)[]
  modifiers?: (number | string)[]
  ignored_numbers?: (number | string)[]
  conditions?: ActionCondition[]
  inline?: boolean
}

export type Field =
  | SelectField
  | MultiSelectField
  | NumberField
  | CalculationField
  | ChanceField

export interface ContextField {
  [id: string]: string
}

export interface AvailableActionData {
  id: number
  game: number
  faction: number
  name: string
  position: number
  schema: Field[]
  context: ContextField
  identifier: string
}

class AvailableAction {
  id: number
  game: number
  faction: number
  name: string
  position: number
  schema: Field[]
  context: ContextField
  identifier: string

  constructor(data: AvailableActionData) {
    this.id = data.id
    this.game = data.game
    this.faction = data.faction
    this.name = data.name
    this.position = data.position
    this.schema = data.schema
    this.context = data.context
    this.identifier = data.identifier
  }
}

export default AvailableAction
