import { Component } from 'react';
import TitleBanner from "../components/TitleBanner.js";
import "./JoinGame.css";
import { Link } from "react-router-dom";
import request from "../helpers/RequestHelper.js"

class JoinGame extends Component {

  constructor(props) {
    super(props);
    this.state = { gamesList: [] };
    this.componentDidMount = this.componentDidMount.bind(this);
  }

  async componentDidMount() {
    const response = await request('get', 'games/', this.props.accessToken, this.props.refreshToken, this.props.setAuthData);
    if (response) {
      this.setState({ gamesList: response.data });
    }
  }

  renderGames = () => {
    const gamesList = this.state.gamesList;
    if (gamesList && gamesList.length > 0) {
      return gamesList.map(game => (<div className="game-list_item" key={game.name}>{game.name}</div>));
    } else {
      return 'None'
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
    );
  }
}

export default JoinGame;
