import { Component } from 'react';
import TopBar from "../../components/TopBar.tsx"
import { Link } from "react-router-dom";

import "./index.css";
import SenatorPortrait from "../../components/SenatorPortrait/index.tsx";


class GamePage extends Component {
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
              <SenatorPortrait name="Fabius" borderColor="red" bgColor="#d06666" majorOffice="Rome Consul" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="yellow" bgColor="#ffbf00" majorOffice="Field Consul" />
              <SenatorPortrait name="Valerius" borderColor="#28ce00" bgColor="#66b266" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="#00daca" bgColor="#4ca7a1" factionLeader={true} />
              <SenatorPortrait name="Valerius" borderColor="#0062ff" bgColor="#4c6bb7" />
              <SenatorPortrait name="Fabius" borderColor="#ba00ba" bgColor="#a24ca2" majorOffice="Censor" />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" />
              <SenatorPortrait name="Fabius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Valerius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
            </div>
            <div className="container">
              <SenatorPortrait name="Cornelius" borderColor="#00daca" bgColor="#4ca7a1" factionLeader={true} />
              <SenatorPortrait name="Valerius" borderColor="#0062ff" bgColor="#4c6bb7" />
              <SenatorPortrait name="Cornelius" borderColor="yellow" bgColor="#ffbf00" majorOffice="Field Consul" />
              <SenatorPortrait name="Valerius" borderColor="#28ce00" bgColor="#66b266" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" />
              <SenatorPortrait name="Fabius" borderColor="red" bgColor="#d06666" majorOffice="Rome Consul" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Valerius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Fabius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Fabius" borderColor="#ba00ba" bgColor="#a24ca2" majorOffice="Censor" />
            </div>
            <div className="container">
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" />
              <SenatorPortrait name="Valerius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Fabius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Fabius" borderColor="red" bgColor="#d06666" majorOffice="Rome Consul" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="yellow" bgColor="#ffbf00" majorOffice="Field Consul" />
              <SenatorPortrait name="Valerius" borderColor="#28ce00" bgColor="#66b266" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="#00daca" bgColor="#4ca7a1" factionLeader={true} />
              <SenatorPortrait name="Valerius" borderColor="#0062ff" bgColor="#4c6bb7" />
              <SenatorPortrait name="Fabius" borderColor="#ba00ba" bgColor="#a24ca2" majorOffice="Censor" />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
            </div>
            <div className="container">
              <SenatorPortrait name="Valerius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Cornelius" borderColor="#00daca" bgColor="#4ca7a1" factionLeader={true} />
              <SenatorPortrait name="Valerius" borderColor="#28ce00" bgColor="#66b266" factionLeader={true} />
              <SenatorPortrait name="Fabius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Cornelius" borderColor="yellow" bgColor="#ffbf00" majorOffice="Field Consul" />
              <SenatorPortrait name="Fabius" borderColor="red" bgColor="#d06666" majorOffice="Rome Consul" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" />
              <SenatorPortrait name="Valerius" borderColor="#0062ff" bgColor="#4c6bb7" />
              <SenatorPortrait name="Fabius" borderColor="#ba00ba" bgColor="#a24ca2" majorOffice="Censor" />
            </div>
            <div className="container">
              <SenatorPortrait name="Fabius" borderColor="#ba00ba" bgColor="#a24ca2" majorOffice="Censor" />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" />
              <SenatorPortrait name="Valerius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Fabius" borderColor="red" bgColor="#d06666" majorOffice="Rome Consul" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="yellow" bgColor="#ffbf00" majorOffice="Field Consul" />
              <SenatorPortrait name="Valerius" borderColor="#28ce00" bgColor="#66b266" factionLeader={true} />
              <SenatorPortrait name="Cornelius" borderColor="#00daca" bgColor="#4ca7a1" factionLeader={true} />
              <SenatorPortrait name="Valerius" borderColor="#0062ff" bgColor="#4c6bb7" />
              <SenatorPortrait name="Fabius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
              <SenatorPortrait name="Cornelius" borderColor="#eaeaea" bgColor="#bebebe" dead={true} />
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default GamePage;
