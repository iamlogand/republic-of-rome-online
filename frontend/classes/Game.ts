import { deserializeToInstance } from "@/functions/serialize"
import User from "@/classes/User"

interface GameData {
  id: number
  name: string
  host: string
  description: string | null
  creation_date: string
  start_date: string | null
}

class Game {
  id: number
  name: string
  host: User | null
  description: string | null
  creation_date: Date
  start_date: Date | null

  constructor(data: GameData) {
    this.id = data.id
    this.name = data.name
    this.host = deserializeToInstance<User>(User, data.host)  // Expects user to be preloaded with game participant
    this.description = data.description
    this.creation_date = new Date(data.creation_date)
    this.start_date = data.start_date ? new Date(data.start_date) : null
  }
}

export default Game
