export interface WarData {
  game_id: number
  name: string
  series_name?: string | null
  index: number
  land_strength: number
  fleet_support: number
  naval_strength: number
  disaster_numbers: number[]
  standoff_numbers: number[]
  spoils: number
  famine: boolean
  status: "Inactive" | "Imminent" | "Active" | "Defeated"
  undefeated_navy: boolean
  unprosecuted: boolean
}

class War {
  gameId: number
  name: string
  seriesName?: string | null
  index: number
  landStrength: number
  fleetSupport: number
  navalStrength: number
  disasterNumbers: number[]
  standoffNumbers: number[]
  spoils: number
  famine: boolean
  status: "Inactive" | "Imminent" | "Active" | "Defeated"
  undefeatedNavy: boolean
  unprosecuted: boolean

  constructor(data: WarData) {
    this.gameId = data.game_id
    this.name = data.name
    this.seriesName = data.series_name ?? null
    this.index = data.index
    this.landStrength = data.land_strength
    this.fleetSupport = data.fleet_support
    this.navalStrength = data.naval_strength
    this.disasterNumbers = data.disaster_numbers
    this.standoffNumbers = data.standoff_numbers
    this.spoils = data.spoils
    this.famine = data.famine
    this.status = data.status
    this.undefeatedNavy = data.undefeated_navy
    this.unprosecuted = data.unprosecuted
  }
}

export default War
