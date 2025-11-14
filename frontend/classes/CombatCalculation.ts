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
  auto_transformed?: boolean
}

class CombatCalculation {
  id: number | "proposal" | null
  game: number
  name: string
  commander: number | null
  war: number | null
  battle: "land" | "naval"
  regularLegions: number
  veteranLegions: number
  fleets: number
  autoTransformed: boolean

  constructor(data: CombatCalculationData) {
    this.id = data.id
    this.game = data.game
    this.name = data.name
    this.commander = data.commander
    this.war = data.war
    this.battle = data.land_battle ? "land" : "naval"
    this.regularLegions = data.regular_legions
    this.veteranLegions = data.veteran_legions
    this.fleets = data.fleets
    this.autoTransformed = data.auto_transformed ?? false
  }
}

export default CombatCalculation
