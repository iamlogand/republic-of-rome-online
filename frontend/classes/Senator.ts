import Faction from "@/types/Faction";
import MajorOffice from "@/types/MajorOffice";
import Praenomen from "@/types/Praenomen";
import Colors from "@/data/colors.json";
import FactionNames from "@/data/factionNames.json";
import getPraenomenAbbr from "@/functions/praenomen";

type Name = 'cornelius' | 'fabius' | 'valerius' | 'julius' | 'claudius' | 'manlius';

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

  getShortName = () => {
    return getPraenomenAbbr(this.praenomen) + " " + this.name
  }
}

export default Senator