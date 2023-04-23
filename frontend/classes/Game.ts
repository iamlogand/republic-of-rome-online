interface GameData {
  id: string;
  name: string;
  owner: string | null;
  description: string | null;
  creation_date: string;
  start_date: string | null;
}

class Game {
  id: string;
  name: string;
  owner: string | null;
  description: string | null;
  creation_date: Date;
  start_date: Date | null;

  constructor(data: GameData) {
    this.id = data.id;
    this.name = data.name;
    this.owner = data.owner;
    this.description = data.description;
    this.creation_date = new Date(data.creation_date);
    this.start_date = data.start_date ? new Date(data.start_date) : null;
  }
}

export default Game;
