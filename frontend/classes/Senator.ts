import numberToRoman from "@/functions/romanNumerals"

interface SenatorData {
  id: number
  name: string
  game: number
  faction: number
  death_step: number | null
  code: number
  generation: number
  rank: number | null
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
  id: number
  name: string
  game: number
  faction: number
  alive: boolean
  code: number
  generation: number
  rank: number | null
  military: number
  oratory: number
  loyalty: number
  influence: number
  popularity: number
  knights: number
  talents: number
  votes: number

  logsFetched: boolean = false

  constructor(data: SenatorData) {
    this.id = data.id
    this.name = data.name
    this.game = data.game
    this.alive = data.death_step === null // Senator is alive if death_step is null (a simplification compared to the backend)
    this.code = data.code
    this.generation = data.generation
    this.rank = data.rank
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
    return (
      this.name +
      (this.generation > 1 ? " " + numberToRoman(this.generation) : "")
    )
  }
}

export default Senator
