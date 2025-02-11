export interface FactionData {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  card_count: number
  status: string[]
}

class Faction {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  card_count: number
  status: string[]

  constructor(data: FactionData) {
    this.id = data.id
    this.player = data.player
    this.position = data.position
    this.card_count = data.card_count
    this.status = data.status
  }
}

export default Faction
