import TopBar from "../../components/TopBar"
import { Link } from "react-router-dom";

import "./index.css";
import SenatorPortrait from "../../components/SenatorPortrait/index";
import Senator from "../../objects/Senator";

const cornelius1 = new Senator("cornelius");
const fabius1 = new Senator("fabius");
const valerius1 = new Senator("valerius");

const fabiusRomeConsul = new Senator("valerius", true, 1, "rome consul", true);
const valeriusFieldConsul = new Senator("valerius", true, 1, "field consul", true);
const corneliusCensor = new Senator("valerius", true, 1, "censor", true);
const valeriusDead = new Senator("valerius", false);

interface GamePageProps {
  username: string;
}

const GamePage = (props: GamePageProps) => {
  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div id="wide_page">
        <div id="page_content">
          <h1>Republic of Rome Online</h1>
          <div>
            <Link to="/">Back to Main Menu</Link>
          </div>
          <h2>Conceptual UI with Sample Data</h2>
          <div className="container">
            <SenatorPortrait senator={cornelius1} borderColor="#ba00ba" bgColor="#a24ca2" />
            <SenatorPortrait senator={fabiusRomeConsul} borderColor="#ba00ba" bgColor="#a24ca2" />
            <SenatorPortrait senator={valeriusFieldConsul} borderColor="#00daca" bgColor="#4ca7a1" />
            <SenatorPortrait senator={corneliusCensor} borderColor="red" bgColor="#d06666" />
            <SenatorPortrait senator={fabius1} borderColor="yellow" bgColor="#ffbf00" />
            <SenatorPortrait senator={cornelius1} borderColor="#28ce00" bgColor="#66b266" />
            <SenatorPortrait senator={valerius1} borderColor="#00daca" bgColor="#4ca7a1" />
            <SenatorPortrait senator={fabius1} borderColor="#0062ff" bgColor="#4c6bb7"/>
            <SenatorPortrait senator={cornelius1} borderColor="#eaeaea" bgColor="#bebebe" />
            <SenatorPortrait senator={valeriusDead} borderColor="#eaeaea" bgColor="#bebebe" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default GamePage;
