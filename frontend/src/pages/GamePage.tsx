import TopBar from "../components/TopBar"
import { Link } from "react-router-dom";
import "./GamePage.css";
import SenatorPortrait from "../components/Senator/SenatorPortrait";
import SenatorName from "../components/Senator/SenatorName";
import Senator from '../objects/Senator';
import { useEffect, useState } from "react";
import axios from "axios";
import SenatorSummary from "../components/Senator/SenatorSummary";

interface GamePageProps {
  username: string;
}

const GamePage = (props: GamePageProps) => {

  const [senators, setSenators] = useState<Senator[]>([]);
  const [summaryRef, setSummaryRef] = useState<any>(null);  // Props for the Summary component

  useEffect(() => {
    axios.get("/SampleGame.json").then(response => {
      let objects = response.data.senators;
      let senators: Senator[] = [];
      for (let i = 0; i < objects.length; i++) {
        const senator: Senator = new Senator(
          objects[i].name,
          objects[i].alive,
          objects[i].faction,
          objects[i].factionLeader,
          objects[i].majorOffice
        );
        senators.push(senator)
      }
      setSenators(senators);
    });
  }, []);

  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div id="wide_page">
        {senators.length > 0 &&
          <div id="page_content">
            <h1>Republic of Rome Online</h1>
            <div>
              <Link to="/">Back to Main Menu</Link>
            </div>
              <h2>Examples of the "Senator Name" component</h2>
              <p>
                Sometimes senators may be referred to by name within a body of text, for example:
                The leader of the Cyan faction is called <SenatorName senator={senators[7]} setSummaryRef={setSummaryRef} />. This <SenatorName senator={senators[7]} setSummaryRef={setSummaryRef} /> is joined by <SenatorName senator={senators[8]} setSummaryRef={setSummaryRef} />, <SenatorName senator={senators[9]} setSummaryRef={setSummaryRef} />, <SenatorName senator={senators[10]} setSummaryRef={setSummaryRef} /> again, <SenatorName senator={senators[11]} setSummaryRef={setSummaryRef} /> the Censor
                and <SenatorName senator={senators[12]} setSummaryRef={setSummaryRef} />.
                If only I had added more than four senators!</p>
              <p>There are only three senators in the red faction:</p>
              <ul>
                <li><SenatorName senator={senators[0]} setSummaryRef={setSummaryRef} /></li>
                <li><SenatorName senator={senators[1]} setSummaryRef={setSummaryRef} /></li>
                <li><SenatorName senator={senators[2]} setSummaryRef={setSummaryRef} /></li>
              </ul>
              <p>Some senators, such as <SenatorName senator={senators[21]} setSummaryRef={setSummaryRef} /> and <SenatorName senator={senators[22]} setSummaryRef={setSummaryRef} /> are dead. Others like <SenatorName senator={senators[18]} setSummaryRef={setSummaryRef} /> and <SenatorName senator={senators[19]} setSummaryRef={setSummaryRef} /> are unaligned.</p>
            <h2>Examples of the "Senator Portrait" component </h2>
            <div className="container">
              {senators.map((senator, index) => <SenatorPortrait 
                key={index}
                senator={senator}
                setSummaryRef={setSummaryRef} /> )}
            </div>
          </div>
        }
      </div>
      {summaryRef && <SenatorSummary {...summaryRef} />}
    </div>
  )
}

export default GamePage;
