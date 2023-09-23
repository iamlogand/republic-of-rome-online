import Colors from "@/data/colors.json"

export type FactionPosition = 1 | 2 | 3 | 4 | 5 | 6

interface FactionData {
  id: number,
  game: number,
  position: FactionPosition,
  player: number,
  rank: number | null
}

class Faction {
  id: number
  game: number
  position: FactionPosition
  player: number
  rank: number | null

  constructor(data: FactionData) {
    this.id = data.id
    this.game = data.game
    this.position = data.position
    this.player = data.player
    this.rank = data.rank
  }
  
  // Get the faction's color hex code
  getColor = (type: "primary" | "bg" | "bgHover" | "textBg" = "primary") => {
    return Colors.aligned[type][this.position]
  }

  // Get the faction's color name (e.g. "Red")
  getName = () => {
    return Colors.aligned["name"][this.position]
  }
}

export default Faction
