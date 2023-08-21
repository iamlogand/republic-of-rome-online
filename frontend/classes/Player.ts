import User from "@/classes/User"
import { deserializeToInstance } from "@/functions/serialize"

interface PlayerData {
  id: number
  user: string
  game: number
  join_date: string
}

class Player {
  id: number
  user: User | null
  game: number
  joinDate: Date

  constructor(data: PlayerData) {
    this.id = data.id
    this.user = deserializeToInstance<User>(User, data.user)  // Expects user to be preloaded with game player
    this.game = data.game
    this.joinDate = new Date(data.join_date)
  }
}

export default Player
