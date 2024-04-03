import getNumberSuffix from "@/functions/numberSuffix"

interface IWar {
  id: number
  name: string
  index: number
  game: number
  land_strength: number
  fleet_support: number
  naval_strength: number
  disaster_numbers: number[]
  standoff_numbers: number[]
  spoils: number
  status: string
  undefeated_navy: boolean
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
  undefeatedNavy: boolean
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
    this.undefeatedNavy = data.undefeated_navy
    this.famine = data.famine
  }

  // Unformatted name of the war
  getName() {
    if (this.index === 0) return `${this.name} War`
    return `${this.index}${getNumberSuffix(this.index)} ${this.name} War`
  }
}

export default War
