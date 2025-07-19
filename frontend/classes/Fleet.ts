export interface FleetData {
  id: number
  game: number
  number: number
  name: string
  campaign: number | null
}

class Fleet {
  id: number
  game: number
  number: number
  name: string
  campaign: number | null

  constructor(data: FleetData) {
    this.id = data.id
    this.game = data.game
    this.number = data.number
    this.name = data.name
    this.campaign = data.campaign
  }
}

export default Fleet
