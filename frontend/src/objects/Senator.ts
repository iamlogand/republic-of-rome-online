import MajorOffice from "../types/MajorOffice";
import Faction from "../types/Faction";
import Colors from "../data/Colors.json";
import FactionNames from "../data/FactionNames.json";
import Praenomen from "../types/Praenomen";

type Name = 'cornelius' | 'fabius' | 'valerius' | 'julius';

class Senator {
  praenomen: Praenomen;
  name: Name;
  alive: boolean;
  faction: Faction;
  factionLeader: boolean;
  majorOffice: MajorOffice;

  constructor(
    praenomen: Praenomen,
    name: Name,
    alive: boolean,
    faction: Faction,
    factionLeader: boolean,
    majorOffice: MajorOffice,
  ) {
    this.praenomen = praenomen;
    this.name = name;
    this.alive = alive;
    this.faction = faction;
    this.factionLeader = factionLeader;
    this.majorOffice = majorOffice;
  }

  getColor = (type: "primary" | "bg") => {
    if (!this.alive) {
      return Colors.dead[type]
    } else if (!this.faction) {
      return Colors.unaligned[type]
    } else {
      return Colors.aligned[type][this.faction];
    }
  }

  getFactionName = () => {
    if (this.alive && this.faction) {
      return FactionNames[this.faction];
    } else {
      return null
    }
  }
}

export default Senator