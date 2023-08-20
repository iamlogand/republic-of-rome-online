interface PotentialActionData {
  id: number
  step: number
  faction: number
  type: string
  required: boolean
}

class PotentialAction {
  id: number
  step: number
  faction: number
  type: string
  required: boolean

  constructor(data: PotentialActionData) {
    this.id = data.id
    this.step = data.step
    this.faction = data.faction
    this.type = data.type
    this.required = data.required
  }
}

export default PotentialAction
