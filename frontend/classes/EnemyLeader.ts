export interface EnemyLeaderData {
  id: number
  game: number
  name: string
  series_name: string
  strength: number
  disaster_number: number
  standoff_number: number
  active: boolean
}

class EnemyLeader {
  id: number
  game: number
  name: string
  seriesName: string
  strength: number
  disasterNumber: number
  standoffNumber: number
  active: boolean

  constructor(data: EnemyLeaderData) {
    this.id = data.id
    this.game = data.game
    this.name = data.name
    this.seriesName = data.series_name
    this.strength = data.strength
    this.disasterNumber = data.disaster_number
    this.standoffNumber = data.standoff_number
    this.active = data.active
  }
}

export default EnemyLeader
