import User from "@/classes/User"
import { deserializeToInstance } from "@/functions/serialize"

interface GameParticipantData {
  id: string
  user: string
  game: string
  join_date: string
}

class GameParticipant {
  id: string
  user: User | null
  game: string
  joinDate: Date

  constructor(data: GameParticipantData) {
    this.id = data.id
    this.user = deserializeToInstance<User>(User, data.user)  // Expects user to be preloaded with game participant
    this.game = data.game
    this.joinDate = new Date(data.join_date)
  }
}

export default GameParticipant
