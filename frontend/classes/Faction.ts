export interface FactionData {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  card_count: number
}

class Faction {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  card_count: number

  constructor(data: FactionData) {
    this.id = data.id
    this.player = data.player
    this.position = data.position
    this.card_count = data.card_count
  }
}

export default Faction
