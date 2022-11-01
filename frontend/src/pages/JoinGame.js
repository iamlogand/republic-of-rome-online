import { Component } from 'react';
import TitleBanner from "../components/TitleBanner.js";
import "./JoinGame.css";
import { Link } from "react-router-dom";
import axios from "axios";

class JoinGame extends Component {

  constructor(props) {
    super(props);
    this.state = {gamesList: []};
    this.componentDidMount = this.componentDidMount.bind(this);
  }

  async componentDidMount() {
    axios.get(process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/games/', {
      headers: {
        "Authorization": "Bearer " + this.props.accessToken
      }
    }).then(response => {

      this.setState({
        gamesList: response.data
      });

    }).catch(error => {
      console.log(error)
    });
  }

  renderGames = () => {
    const gamesList = this.state.gamesList;
    return gamesList.map(game => (<div className="game-list_item" key={game.name}>{game.name}</div>));
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
