interface ActionLogData {
  id: number
  index: number
  step: number
  type: string
  faction: number | null
  data: string
  creation_date: string
}

class ActionLog {
  id: number
  index: number
  step: number
  type: string
  faction: number | null
  data: any
  creation_date: Date

  constructor(data: ActionLogData) {
    this.id = data.id
    this.index = data.index
    this.step = data.step
    this.type = data.type
    this.faction = data.faction
    this.data = data.data
    this.creation_date = new Date(data.creation_date)
  }
}

export default ActionLog
