import Colors from "@/data/colors.json"
import { FactionPosition } from "@/classes/Faction"

interface FamilySenatorData {
  id: number,
  name: string,
  game: number,
  faction: number
}

class FamilySenator {
  id: number;
  name: string;
  game: number;
  faction: number;

  constructor(data: FamilySenatorData) {
    this.id = data.id;
    this.name = data.name;
    this.game = data.game;
    this.faction = data.faction;
  }
}

export default FamilySenator
