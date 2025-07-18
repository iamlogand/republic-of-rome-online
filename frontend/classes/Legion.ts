export interface LegionData {
  id: number
  game: number
  number: number
  veteran: boolean
  allegiance: number | null
  name: string
  strength: number
  campaign: number | null
}

class Legion {
  id: number
  game: number
  number: number
  veteran: boolean
  allegiance: number | null
  name: string
  strength: number
  campaign: number | null

  constructor(data: LegionData) {
    this.id = data.id
    this.game = data.game
    this.number = data.number
    this.veteran = data.veteran
    this.allegiance = data.allegiance
    this.name = data.name
    this.strength = data.strength
    this.campaign = data.campaign
  }
}

export default Legion
