import TopBar from "../components/TopBar"
import { Link } from "react-router-dom";

import "./GamePage.css";
import SenatorPortrait from "../components/Senator/SenatorPortrait";
import Senator from "../objects/Senator";

const senators = [
  new Senator("cornelius", true, 1, true, "rome consul"),
  new Senator("fabius", true, 1),
  new Senator("valerius", true, 1),
  new Senator("fabius", true, 2, true),
  new Senator("valerius", true, 2),
  new Senator("valerius", true, 3, true),
  new Senator("cornelius", true, 3),
  new Senator("fabius", true, 4, true),
  new Senator("cornelius", true, 4),
  new Senator("valerius", true, 4),
  new Senator("cornelius", true, 4),
  new Senator("fabius", true, 4, false, "censor"),
  new Senator("fabius", true, 4),
  new Senator("valerius", true, 5, true),
  new Senator("fabius", true, 5),
  new Senator("valerius", true, 6, true),
  new Senator("cornelius", true, 6),
  new Senator("valerius", true, 6, false, "field consul"),
  new Senator("cornelius", true),
  new Senator("fabius", true),
  new Senator("valerius", true),
  new Senator("cornelius", false),
  new Senator("fabius", false),
  new Senator("cornelius", false),
  new Senator("fabius", false)
];

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
            {senators.map((senator, index) => <SenatorPortrait senator={senator} key={index} />)}
          </div>
        </div>
      </div>
    </div>
  )
}

export default GamePage;
