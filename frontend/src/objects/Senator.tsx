type Name = 'cornelius' | 'fabius' | 'valerius';
type Faction = null | 1 | 2 | 3 | 4 | 5 | 6;
type MajorOffice = null | 'rome consul' | 'field consul' | 'censor';

class Senator {
    name: Name;
    alive: boolean;
    faction: Faction;
    factionLeader: boolean;
    majorOffice: MajorOffice;

    constructor(
        name: Name,
        alive: boolean = true,
        faction: Faction = null,
        majorOffice: MajorOffice = null,
        factionLeader: boolean = false
    ) {
        this.name = name;
        this.alive = alive;
        this.faction = faction;
        this.majorOffice = majorOffice;
        this.factionLeader = factionLeader;
    }
}

export default Senator