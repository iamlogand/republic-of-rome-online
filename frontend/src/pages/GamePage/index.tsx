import TopBar from "../../components/TopBar"
import { Link } from "react-router-dom";

import "./index.css";
import SenatorPortrait from "../../components/SenatorPortrait/index";
import Senator from "../../objects/Senator";

const cornelius = new Senator("cornelius");

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
            <SenatorPortrait senator={cornelius} borderColor="red" bgColor="#d06666" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default GamePage;
