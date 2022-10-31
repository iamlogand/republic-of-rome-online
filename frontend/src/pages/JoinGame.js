import { Component } from 'react';
import TitleBanner from "../components/TitleBanner.js";
import "./JoinGame.css";
import { Link } from "react-router-dom";
import axios from "axios";

class JoinGame extends Component {
  constructor(props) {
    super(props);
    this.state = {
      gamesList: [],
      gamesListResponseCode: null
    };
  }

  async componentDidMount() {
    try {
      const gamesList = (await axios.get(process.env.REACT_APP_BACKEND_ORIGIN + '/api/games/')).data;
      this.setState({
        gamesList: gamesList,
        gamesListResponseCode: null
      });
    } catch (AxiosError) {
      console.log(AxiosError);
      this.setState({
        gamesList: [],
        gamesListResponseCode: AxiosError.response.status
      });
    }
  }

  renderGames = () => {
    const gamesList = this.state.gamesList;
    const errorCode = this.state.gamesListResponseCode;
    if (gamesList.length > 0) {
      return gamesList.map(game => (<div className="game-list_item" key={game.name}>{game.name}</div>));
    } else if (errorCode == '403') {
      return <div>Please login to see existing games</div>;
    }
  }

  render() {
    return (
      <div>
        <TitleBanner />
        <div className='back'>
          <Link to="..">Back to Main Menu</Link>
        </div>
        <div className="game-list">
          <h3>Existing Games:</h3>
          {this.renderGames()}
        </div>
      </div>
    )
  }
}

export default JoinGame;
