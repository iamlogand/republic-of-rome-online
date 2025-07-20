export interface CombatCalculationData {
  id: string
  name: string
  commander: number | null
  war: number | null
  battle: "Land" | "Naval"
  legions: number
  veteranLegions: number
  fleets: number
}

class CombatCalculation {
  id: string
  name: string
  commander: number | null
  war: number | null
  battle: "Land" | "Naval"
  legions: number
  veteranLegions: number
  fleets: number

  constructor(data: CombatCalculationData) {
    this.id = data.id
    this.name = data.name
    this.commander = data.commander
    this.war = data.war
    this.battle = data.battle
    this.legions = data.legions
    this.veteranLegions = data.veteranLegions
    this.fleets = data.fleets
  }
}

export default CombatCalculation
