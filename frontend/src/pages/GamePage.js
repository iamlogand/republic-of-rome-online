import { Component } from 'react';
import TopBar from "../components/TopBar.js"
import { Link } from "react-router-dom";
import SenatorPortrait from "../components/SenatorPortrait/index.js";
import "./GamePage.css";

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
            <div className="container">
              <SenatorPortrait borderColor="red" bgColor="#d06666" factionLeader={true} majorOffice="Rome Consul" />
              <SenatorPortrait borderColor="yellow" bgColor="#e5b700" factionLeader={true} majorOffice="Field Consul" />
              <SenatorPortrait borderColor="#28ce00" bgColor="#66b266" factionLeader={true} />
              <SenatorPortrait borderColor="#00daca" bgColor="#4ca7a1" />
            </div>
            <div className="container">
              <SenatorPortrait borderColor="#004aff" bgColor="#4c6bb7" />
              <SenatorPortrait borderColor="#ba00ba" bgColor="#a24ca2" factionLeader={true} majorOffice="Censor" />
              <SenatorPortrait borderColor="white" bgColor="#eeeeee" />
              <SenatorPortrait dead={true} />
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Game;
