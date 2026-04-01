export interface GameData {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
  password: string
  created_on: string
  started_on?: string
  finished_on?: string
  factions?: [
    {
      player: {
        id: number
        username: string
      }
    },
  ]
  step: number
  turn: number
  phase: string
  sub_phase: string
  state_treasury: number
  unrest: number
  current_proposal: string
  defeated_proposals: string[]
  votes_nay: number
  votes_yea: number
  concessions: string[]
  available_concessions: string[]

  has_password: boolean
  status: string
  votes_pending: number
  deck_count: number
  famine_severity: number
  unprosecuted_wars: number
}

class Game {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
  password: string
  createdOn: string
  startedOn?: string
  finishedOn?: string
  factions?: [
    {
      player: {
        id: number
        username: string
      }
    },
  ]
  step: number
  turn: number
  phase: string
  subPhase: string
  stateTreasury: number
  unrest: number
  currentProposal: string
  defeatedProposals: string[]
  votesNay: number
  votesYea: number
  concessions: string[]
  availableConcessions: string[]

  hasPassword: boolean
  status: string
  votesPending: number
  deckCount: number
  famineSeverity: number
  unprosecutedWars: number

  constructor(data: GameData) {
    this.id = data.id
    this.name = data.name
    this.host = data.host
    this.password = data.password
    this.createdOn = data.created_on
    this.startedOn = data.started_on
    this.finishedOn = data.finished_on
    this.factions = data.factions
    this.step = data.step
    this.turn = data.turn
    this.phase = data.phase
    this.subPhase = data.sub_phase
    this.stateTreasury = data.state_treasury
    this.unrest = data.unrest
    this.currentProposal = data.current_proposal
    this.defeatedProposals = data.defeated_proposals
    this.votesNay = data.votes_nay
    this.votesYea = data.votes_yea
    this.concessions = data.concessions
    this.availableConcessions = data.available_concessions

    this.hasPassword = data.has_password
    this.status = data.status
    this.votesPending = data.votes_pending
    this.deckCount = data.deck_count
    this.famineSeverity = data.famine_severity
    this.unprosecutedWars = data.unprosecuted_wars
  }
}

export default Game
