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
      const res = await fetch('http://rorsiteb-env.eba-q4m3zrnr.eu-west-2.elasticbeanstalk.com/api/games/');
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
        <h1>React UI</h1>
        <p>List of games:</p>
        <ul>
          {this.renderGames()}
        </ul>
      </div>
    )
  }
}

export default App;
