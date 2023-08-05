import Colors from "@/data/colors.json"
import { FactionPosition } from "@/classes/Faction"

interface FamilySenatorData {
  id: string,
  name: string,
  game: string,
  faction: string
}

class FamilySenator {
  id: string;
  name: string;
  game: string;
  faction: string;

  constructor(data: FamilySenatorData) {
    this.id = data.id;
    this.name = data.name;
    this.game = data.game;
    this.faction = data.faction;
  }

  getColor = (type: "primary" | "bg", factionPosition: FactionPosition) => {
    return Colors.aligned[type][factionPosition];
  }
}

export default FamilySenator
