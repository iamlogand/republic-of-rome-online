import { Component } from 'react';
import TitleBanner from "../components/TitleBanner.js";
import "./JoinGame.css";
import { Link } from "react-router-dom";

class JoinGame extends Component {
  constructor(props) {
    super(props);
    this.state = {
      gamesList: []
    };
  }

  async componentDidMount() {
    try {
      const res = await fetch(process.env.REACT_APP_BACKEND_ORIGIN + '/api/games/');
      const gamesList = await res.json();
      this.setState({
        gamesList
      });
    } catch (e) {
      console.log(e);
    }
  }

  renderGames = () => {
    return this.state.gamesList.map(game => (<div className="game-list_item" key={game.name}>{game.name}</div>))
  }

  render() {
    return (
      <div>
        <TitleBanner />
        <div className="game-list">
          <h3>Existing Games:</h3>
          {this.renderGames()}
        </div>
        <div className='back'>
          <Link to="..">Back</Link>
        </div>
      </div>
    )
  }
}

export default JoinGame;
