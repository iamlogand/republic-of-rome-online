
import { useEffect, useState } from "react";
import axios from "axios";
import { GetServerSidePropsContext } from "next";
import getInitialCookieData from "@/functions/cookies";
import SenatorName from "../components/senators/SenatorName";
import SenatorInspector from "@/components/senators/SenatorInspector";
import SenatorPortrait from "@/components/senators/SenatorPortrait";
import Senator from '@/classes/Senator';
import styles from "./demo.module.css";
import Head from "next/head";
import { useAuthContext } from "@/contexts/AuthContext";
import PageError from "@/components/PageError";
import Breadcrumb from "@/components/Breadcrumb";

// This page is probably temporary because it's just a sandbox for some UI components.
const DemoPage = () => {
  const { username } = useAuthContext();
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

  // Render page error if user is not signed in
  if ( username == '') {
    return <PageError statusCode={401} />;
  }

  return (
    <>
      <Head>
        <title>Demo | Republic of Rome Online</title>
      </Head>
      <main>
        <Breadcrumb />
        <h2>Demo</h2>

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
    </>
  )
}

export default DemoPage;

export const getServerSideProps = async (context: GetServerSidePropsContext) => {
  const { clientAccessToken, clientRefreshToken, clientUsername } = getInitialCookieData(context);
  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUsername: clientUsername
    }
  };
};
