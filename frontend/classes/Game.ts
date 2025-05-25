export interface GameData {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
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
  status: string
  step: number
  turn: number
  phase: string
  sub_phase: string
  state_treasury: number
  unrest: number
  current_proposal: string
}

class Game {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
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
  status: string
  step: number
  turn: number
  phase: string
  subPhase: string
  stateTreasury: number
  unrest: number
  currentProposal: string

  constructor(data: GameData) {
    this.id = data.id
    this.name = data.name
    this.host = data.host
    this.createdOn = data.created_on
    this.startedOn = data.started_on
    this.finishedOn = data.finished_on
    this.factions = data.factions
    this.status = data.status
    this.step = data.step
    this.turn = data.turn
    this.phase = data.phase
    this.subPhase = data.sub_phase
    this.stateTreasury = data.state_treasury
    this.unrest = data.unrest
    this.currentProposal = data.current_proposal
  }
}

export default Game
