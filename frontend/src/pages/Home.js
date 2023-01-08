import { Component } from 'react';
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar.js"

/**
 * The component for the home page
 */
class Home extends Component {
  render() {
    return (
      <div id="page_container">
        <TopBar username={this.props.username} />
        <div id="standard_page">
          <div id="page_content">
            <h1>Republic of Rome Online</h1>
            <h3>It's not personal, it's only business.</h3>
            <div>
              <h3>Play:</h3>
              <div><Link to="/join-game">Join Game</Link></div>
              <div><Link to="/#">Create Game</Link></div>
              <div><Link to="/game">Mock User Interface</Link></div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Home;
