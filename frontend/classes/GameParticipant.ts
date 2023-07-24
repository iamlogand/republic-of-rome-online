interface GameParticipantData {
  id: string,
  user: string,
  game: string,
  join_date: string
}

class GameParticipant {
  id: string;
  user: string;
  game: string;
  joinDate: Date;

  constructor(data: GameParticipantData) {
    this.id = data.id;
    this.user = data.user;
    this.game = data.game;
    this.joinDate = new Date(data.join_date);
  }
}

export default GameParticipant
