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
          objects[i].praenomen,
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
      <div id="standard_page">
        <header className='row'>
          <Link to=".." className="button" style={{width: "90px"}}>◀&nbsp; Back</Link>
          <h2 className='no-margin'>Game Page</h2>
        </header>
        {senators.length > 0 &&
          <div>
            <h3>Senator Names</h3>
            <ul>
              {senators.map((senator, index) =>
                <li key={index}>
                  Senator {index + 1}: <SenatorName senator={senator} setInspectorRef={setInspectorRef} />
                </li>
              )}
            </ul>
            <h3>Senator Portraits</h3>
            <div className="container">
              {senators.map((senator, index) =>
                <SenatorPortrait key={index} senator={senator} setInspectorRef={setInspectorRef} />
              )}
            </div>
          </div>
        }
      </div>
      {inspectorRef && <SenatorInspector {...inspectorRef} />}
    </div>
  )
}

export default GamePage;
