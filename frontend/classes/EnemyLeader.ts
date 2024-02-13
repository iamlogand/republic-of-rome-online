interface IEnemyLeader {
  id: number
  name: string
  game: number
  strength: number
  disaster_number: number
  standoff_number: number
  war_name: string
  current_war: number
  dead: boolean
}

class EnemyLeader {
  id: number
  name: string
  game: number
  strength: number
  disasterNumber: number
  standoffNumber: number
  warName: string
  currentWar: number
  dead: boolean

  constructor(data: IEnemyLeader) {
    this.id = data.id
    this.name = data.name
    this.game = data.game
    this.strength = data.strength
    this.disasterNumber = data.disaster_number
    this.standoffNumber = data.standoff_number
    this.warName = data.war_name
    this.currentWar = data.current_war
    this.dead = data.dead
  }
}

export default EnemyLeader