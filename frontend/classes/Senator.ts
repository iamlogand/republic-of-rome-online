export interface SenatorData {
  game: number
  name: string
  code: string
  faction: number | null
  alive: boolean
  military: number
  oratory: number
  loyalty: number
  influence: number
  popularity: number
  knights: number
  talents: number
  votes: number
}

class Senator {
  game: number
  name: string
  code: string
  faction: number | null
  alive: boolean
  military: number
  oratory: number
  loyalty: number
  influence: number
  popularity: number
  knights: number
  talents: number
  votes: number

  constructor(data: SenatorData) {
    this.game = data.game
    this.name = data.name
    this.code = data.code
    this.faction = data.faction
    this.alive = data.alive
    this.military = data.military
    this.oratory = data.oratory
    this.loyalty = data.loyalty
    this.influence = data.influence
    this.popularity = data.popularity
    this.knights = data.knights
    this.talents = data.talents
    this.votes = data.votes
  }
}

export default Senator
