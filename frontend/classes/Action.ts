interface ActionData {
  id: number
  step: number
  faction: number
  type: string
  required: boolean
  completed: boolean
}

class Action {
  id: number
  step: number
  faction: number
  type: string
  required: boolean
  completed: boolean

  constructor(data: ActionData) {
    this.id = data.id
    this.step = data.step
    this.faction = data.faction
    this.type = data.type
    this.required = data.required
    this.completed = data.completed
  }
}

export default Action
