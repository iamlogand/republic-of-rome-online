import { Component } from 'react';
import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      gamesList: []
    };
  }

  async componentDidMount() {
    try {
      const res = await fetch(process.env.REACT_APP_BACKEND_ORIGIN + '/games/');
      const gamesList = await res.json();
      this.setState({
        gamesList
      });
    } catch (e) {
      console.log(e);
    }
  }

  renderGames = () => {
    return this.state.gamesList.map(game => (<li key={game.name}>{game.name}</li>))
  }

  render() {
    return (
      <div>
        <h1>Republic of Rome</h1>
        <p>Games:</p>
        <ul>
          {this.renderGames()}
        </ul>
      </div>
    )
  }
}

export default App;
