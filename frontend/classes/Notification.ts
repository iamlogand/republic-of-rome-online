interface NotificationData {
  id: number
  index: number
  step: number
  type: string
  faction: number | null
  data: string
}

class Notification {
  id: number
  index: number
  step: number
  type: string
  faction: number | null
  data: any

  constructor(data: NotificationData) {
    this.id = data.id
    this.index = data.index
    this.step = data.step
    this.type = data.type
    this.faction = data.faction
    this.data = data.data
  }
}

export default Notification
