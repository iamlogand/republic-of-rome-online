
import { useEffect, useState } from "react";
import axios from "axios";
import { GetServerSidePropsContext } from "next";
import getInitialCookieData from "@/functions/cookies";
import Button from "@/components/Button";
import SenatorName from "../components/senator/SenatorName";
import SenatorInspector from "@/components/senator/SenatorInspector";
import SenatorPortrait from "@/components/senator/SenatorPortrait";
import Senator from '@/classes/Senator';
import styles from "./demo.module.css";

const DemoPage = () => {

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
    <main id="standard_page">
      <section className='row'>
        <Button href="..">◀&nbsp; Back</Button>
        <h2>Game Page</h2>
      </section>
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
          <div className={styles.container}>
            {senators.map((senator, index) =>
              <SenatorPortrait key={index} senator={senator} setInspectorRef={setInspectorRef} />
            )}
          </div>
          <div className={styles.container}>
            {senators.map((senator, index) =>
              <SenatorPortrait key={index} senator={senator} setInspectorRef={setInspectorRef} size={100} />
            )}
          </div>
          <div className={styles.container}>
            {senators.map((senator, index) =>
              <SenatorPortrait key={index} senator={senator} setInspectorRef={setInspectorRef} size={150} />
            )}
          </div>
          <div className={styles.container}>
            {senators.map((senator, index) =>
              <SenatorPortrait key={index} senator={senator} setInspectorRef={setInspectorRef} size={200} />
            )}
          </div>
        </div>
      }
      {inspectorRef && <SenatorInspector {...inspectorRef} />}
    </main>
  )
}

export default DemoPage;

export const getServerSideProps = async (context: GetServerSidePropsContext) => {
  const { accessToken, refreshToken, username } = getInitialCookieData(context);
  return {
    props: {
      ssrAccessToken: accessToken,
      ssrRefreshToken: refreshToken,
      ssrUsername: username
    }
  };
};
