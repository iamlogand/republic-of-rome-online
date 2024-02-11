interface IWar {
  id: number
  name: string
  index: number
  game: number
  land_strength: number
  fleet_support: number
  naval_strength: number
  disaster_numbers: any
  standoff_numbers: any
  spoils: number
  status: string
  naval_defeated: boolean
  famine: boolean
}

class War {
  id: number
  name: string
  index: number
  game: number
  landStrength: number
  fleetSupport: number
  navalStrength: number
  disasterNumbers: number[]
  standoffNumbers: number[]
  spoils: number
  status: string
  naval_defeated: boolean
  famine: boolean

  constructor(data: IWar) {
    this.id = data.id
    this.name = data.name
    this.index = data.index
    this.game = data.game
    this.landStrength = data.land_strength
    this.fleetSupport = data.fleet_support
    this.navalStrength = data.naval_strength
    this.disasterNumbers = data.disaster_numbers
    this.standoffNumbers = data.standoff_numbers
    this.spoils = data.spoils
    this.status = data.status
    this.naval_defeated = data.naval_defeated
    this.famine = data.famine
  }

  getName() {
    if (this.index === 0) return `${this.name} War`
    return `${this.index}${this.getSuffix(this.index)} ${this.name} War`
  }

  getSuffix(number: number) {
    if (number === 1) return "st"
    if (number === 2) return "nd"
    if (number === 3) return "rd"
    return "th"
  }
}

export default War
