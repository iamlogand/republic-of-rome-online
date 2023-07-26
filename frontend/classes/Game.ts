interface GameData {
  id: string;
  name: string;
  host: string | null;
  description: string | null;
  creation_date: string;
  start_date: string | null;
  step: number;
}

class Game {
  id: string;
  name: string;
  host: string | null;
  description: string | null;
  creation_date: Date;
  start_date: Date | null;
  step: number;

  constructor(data: GameData) {
    this.id = data.id;
    this.name = data.name;
    this.host = data.host;
    this.description = data.description;
    this.creation_date = new Date(data.creation_date);
    this.start_date = data.start_date ? new Date(data.start_date) : null;
    this.step = data.step;
  }
}

export default Game;
