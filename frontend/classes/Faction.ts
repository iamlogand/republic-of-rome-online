import Colors from "@/data/colors.json"

export type FactionPosition = "1" | "2" | "3" | "4" | "5" | "6"

interface FactionData {
  id: string,
  game: string,
  position: FactionPosition,
  player: string
}

class Faction {
  id: string
  game: string
  position: FactionPosition
  player: string

  constructor(data: FactionData) {
    this.id = data.id
    this.game = data.game
    this.position = data.position
    this.player = data.player
  }
  
  // Get the faction's color hex code
  getColor = () => {
    return Colors.aligned["primary"][this.position];
  }

  // Get the faction's color name (e.g. "Red")
  getName = () => {
    return Colors.aligned["name"][this.position];
  }
}

export default Faction
