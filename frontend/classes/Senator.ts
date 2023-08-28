interface SenatorData {
  id: number,
  name: string,
  game: number,
  faction: number,
  military: number,
  oratory: number,
  loyalty: number,
  influence: number,
  popularity: number,
  knights: number,
  talents: number
}

class Senator {
  id: number
  name: string
  game: number
  faction: number
  military: number
  oratory: number
  loyalty: number
  influence: number
  popularity: number
  knights: number
  talents: number

  constructor(data: SenatorData) {
    this.id = data.id
    this.name = data.name
    this.game = data.game
    this.faction = data.faction
    this.military = data.military
    this.oratory = data.oratory
    this.loyalty = data.loyalty
    this.influence = data.influence
    this.popularity = data.popularity
    this.knights = data.knights
    this.talents = data.talents
  }
}

export default Senator
