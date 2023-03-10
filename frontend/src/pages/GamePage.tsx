import TopBar from "../components/TopBar"
import { Link } from "react-router-dom";
import "./GamePage.css";
import SenatorPortrait from "../components/Senator/SenatorPortrait";
import SenatorName from "../components/Senator/SenatorName";
import Senator from '../objects/Senator';
import { useEffect, useState } from "react";
import axios from "axios";
import SenatorInspector from "../components/Senator/SenatorInspector";

interface GamePageProps {
  username: string;
}

const GamePage = (props: GamePageProps) => {

  const [senators, setSenators] = useState<Senator[]>([]);
  const [inspectorRef, setInspectorRef] = useState<any>(null);  // Props for the Inspector component

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
                The leader of the Cyan faction is called <SenatorName senator={senators[7]} setInspectorRef={setInspectorRef} />. This <SenatorName senator={senators[7]} setInspectorRef={setInspectorRef} /> is joined by <SenatorName senator={senators[8]} setInspectorRef={setInspectorRef} />, <SenatorName senator={senators[9]} setInspectorRef={setInspectorRef} />, <SenatorName senator={senators[10]} setInspectorRef={setInspectorRef} /> again, <SenatorName senator={senators[11]} setInspectorRef={setInspectorRef} /> the Censor
                and <SenatorName senator={senators[12]} setInspectorRef={setInspectorRef} />.
                If only I had added more than four senators!</p>
              <p>There are only three senators in the red faction:</p>
              <ul>
                <li><SenatorName senator={senators[0]} setInspectorRef={setInspectorRef} /></li>
                <li><SenatorName senator={senators[1]} setInspectorRef={setInspectorRef} /></li>
                <li><SenatorName senator={senators[2]} setInspectorRef={setInspectorRef} /></li>
              </ul>
              <p>Some senators, such as <SenatorName senator={senators[21]} setInspectorRef={setInspectorRef} /> and <SenatorName senator={senators[22]} setInspectorRef={setInspectorRef} /> are dead. Others like <SenatorName senator={senators[18]} setInspectorRef={setInspectorRef} /> and <SenatorName senator={senators[19]} setInspectorRef={setInspectorRef} /> are unaligned.</p>
            <h2>Examples of the "Senator Portrait" component </h2>
            <div className="container">
              {senators.map((senator, index) => <SenatorPortrait 
                key={index}
                senator={senator}
                setInspectorRef={setInspectorRef} /> )}
            </div>
          </div>
        }
      </div>
      {inspectorRef && <SenatorInspector {...inspectorRef} />}
    </div>
  )
}

export default GamePage;
