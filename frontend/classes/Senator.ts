import numberToRoman from "@/functions/romanNumerals"

interface SenatorData {
  id: number,
  name: string,
  game: number,
  faction: number,
  alive: boolean,
  code: number,
  generation: number,
  military: number,
  oratory: number,
  loyalty: number,
  influence: number,
  popularity: number,
  knights: number,
  talents: number,
  votes: number
}

class Senator {
  id: number
  name: string
  game: number
  faction: number
  alive: boolean
  code: number
  generation: number
  military: number
  oratory: number
  loyalty: number
  influence: number
  popularity: number
  knights: number
  talents: number
  votes: number

  constructor(data: SenatorData) {
    this.id = data.id
    this.name = data.name
    this.game = data.game
    this.alive = data.alive
    this.code = data.code
    this.generation = data.generation
    this.faction = data.faction
    this.military = data.military
    this.oratory = data.oratory
    this.loyalty = data.loyalty
    this.influence = data.influence
    this.popularity = data.popularity
    this.knights = data.knights
    this.talents = data.talents
    this.votes = data.votes
  }

  get displayName() {
    return this.name + (this.generation > 1 ? " " + numberToRoman(this.generation) : "")
  }
}

export default Senator
