export interface CombatCalculationData {
  id: number | "proposal" | null
  game: number
  name: string
  commander: number | null
  war: number | null
  land_battle: boolean
  regular_legions: number
  veteran_legions: number
  fleets: number
}

class CombatCalculation {
  id: number | "proposal" | null
  game: number
  name: string
  commander: number | null
  war: number | null
  battle: "Land" | "Naval"
  regularLegions: number
  veteranLegions: number
  fleets: number

  constructor(data: CombatCalculationData) {
    this.id = data.id
    this.game = data.game
    this.name = data.name
    this.commander = data.commander
    this.war = data.war
    this.battle = data.land_battle ? "Land" : "Naval"
    this.regularLegions = data.regular_legions
    this.veteranLegions = data.veteran_legions
    this.fleets = data.fleets
  }
}

export default CombatCalculation
