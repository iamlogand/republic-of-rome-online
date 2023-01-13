import { Component } from 'react';
import TopBar from "../components/TopBar.js"
import { Link } from "react-router-dom";
import SenatorPortrait from "../components/SenatorPortrait/index.js";

class Game extends Component {
  render() {
    return (
      <div id="page_container">
        <TopBar username={this.props.username} />
        <div id="wide_page">
          <div id="page_content">
            <h1>Republic of Rome Online</h1>
            <div>
              <Link to="/">Back to Main Menu</Link>
            </div>
            <h2>Conceptual UI with Sample Data</h2>
            <SenatorPortrait color="red" />
            <SenatorPortrait color="orange" majorOffice="consul" />
            <SenatorPortrait color="green" />
            <SenatorPortrait color="#00a79b" />
            <SenatorPortrait color="blue" majorOffice="consul" />
            <SenatorPortrait color="purple" majorOffice="consul" />
            <SenatorPortrait color="grey" />
          </div>
        </div>
      </div>
    )
  }
}

export default Game;
