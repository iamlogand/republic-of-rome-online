export interface ActionSignals {
  [key: string]: string
}

export interface ActionCondition {
  value1: string | number
  operation: "==" | "!=" | ">="
  value2: string | number
}

export interface ActionField {
  type: string
  name: string
  options?: [
    {
      value: string
      name?: string
      object_class?: string
      id?: number
      signals?: ActionSignals
      conditions?: ActionCondition[]
    }
  ]
  min?: (number | string)[]
  max?: (number | string)[]
}

export interface AvailableActionData {
  id: number
  game: number
  faction: number
  name: string
  schema: ActionField[]
}

class AvailableAction {
  id: number
  game: number
  faction: number
  name: string
  schema: ActionField[]

  constructor(data: AvailableActionData) {
    this.id = data.id
    this.game = data.game
    this.faction = data.faction
    this.name = data.name
    this.schema = data.schema
  }
}

export default AvailableAction
