import { useCallback, useEffect, useState } from 'react';
import Head from 'next/head';
import { GetServerSidePropsContext } from 'next';
import useWebSocket from 'react-use-websocket';

import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';

import Game from '@/classes/Game';
import GameParticipant from '@/classes/GameParticipant';
import Faction from '@/classes/Faction';
import FamilySenator from '@/classes/FamilySenator';
import Breadcrumb from '@/components/Breadcrumb';
import PageError from '@/components/PageError';
import getInitialCookieData from '@/functions/cookies';
import request from '@/functions/request';
import { useAuthContext } from '@/contexts/AuthContext';
import { deserializeToInstance, deserializeToInstances } from '@/functions/serialize';
import User from '@/classes/User';
import Collection from '@/classes/Collection';
import SenatorPortrait2 from '@/components/senators/SenatorPortrait2';
import styles from "./play.module.css"

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface PlayGamePageProps {
  clientTimezone: string
  gameId: string
  authFailure: boolean
  initialGame: string
}

// The "Play Game" page component
const PlayGamePage = (props: PlayGamePageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext();

  // Game-specific state
  const [game, setGame] = useState<Game | null>(() =>
    props.initialGame ? deserializeToInstance<Game>(Game, props.initialGame) : null
  );
  const [gameParticipants, setGameParticipants] = useState<Collection<GameParticipant>>(new Collection<GameParticipant>());
  const [factions, setFactions] = useState<Collection<Faction>>(new Collection<Faction>());
  const [familySenators, setFamilySenators] = useState<Collection<FamilySenator>>(new Collection<FamilySenator>());

  // Fetch game participants
  const fetchGameParticipants = useCallback(async () => {
    const response = await request('GET', `game-participants/?game=${props.gameId}&prefetch_user`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<GameParticipant>(GameParticipant, response.data)
      setGameParticipants(new Collection<GameParticipant>(deserializedInstances));
    } else {
      setGameParticipants(new Collection<GameParticipant>());
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch factions
  const fetchFactions = useCallback(async () => {
    const response = await request('GET', `factions/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<Faction>(Faction, response.data)
      setFactions(new Collection<Faction>(deserializedInstances));
    } else {
      setFactions(new Collection<Faction>());
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch family senators
  const fetchFamilySenators = useCallback(async () => {
    const response = await request('GET', `family-senators/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<FamilySenator>(FamilySenator, response.data)
      setFamilySenators(new Collection<FamilySenator>(deserializedInstances));
    } else {
      setFamilySenators(new Collection<FamilySenator>());
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch game participants, factions and family senators once on initial render
  useEffect(() => {
    fetchGameParticipants()
    fetchFactions()
    fetchFamilySenators()
  }, [fetchGameParticipants, fetchFactions, fetchFamilySenators])
  
  // Render page error if user is not signed in
  if (user === null || props.authFailure) {
    return <PageError statusCode={401} />;
  } else if (game === null || game.step < 1) {
    return <PageError statusCode={404} />
  }

  return (
    <>
      <Head>
        <title>{game ? `Playing ${game.name} | Republic of Rome Online` : 'Loading... | Republic of Rome Online'}</title>
      </Head>
      <main className={styles.playPage}>
        <div className={styles.layout}>
          <Card variant="outlined" className={`${styles.section} ${styles.metaSection}`}>
            <section>
              <b>Meta section</b> - will contain turn number, phase, state treasury and some info about your faction (like color, vote count, total influence, faction treasury) 
            </section>
          </Card>
          <div className={styles.sections}>
            <Card variant="outlined" className={`${styles.section} ${styles.normalSection}`}>
              <section>
              <b>Detail section</b> - will be blank by default, but when you click on entities like senators, factions, wars this section will contain detailed info about the selected entity. 
              </section>
            </Card>
            <Card variant="outlined" className={`${styles.section} ${styles.normalSection} ${styles.mainSection}`}>
              <section className={styles.sectionContent}>
                <p style={{ marginTop: 0 }}>
                  <b>Main section</b> - will contain several tabs, with each being about a specific topic, such as my faction, all senators, all factions, the senate (for the senate phase), provinces, warfare and (one day) a map.
                </p>
                <p>For now there is just the senators in the game:</p>
                <Stack direction="row" spacing={2} useFlexGap flexWrap="wrap">
                    {factions.asArray.map((faction: Faction) => {
                      const user = gameParticipants.byId[faction.player]?.user
                      if (user && user instanceof User) {
                        return (
                          <div key={faction.id}>
                            <h4 style={{marginTop: 0, marginBottom: 10}}>Faction of {user?.username}</h4>
                            <Stack direction="row" spacing={1}>
                              {familySenators.filterByAttribute('faction', faction.id).map((senator: FamilySenator) => {
                                return <SenatorPortrait2 key={senator.id} senator={senator} faction={faction} />
                              })}
                            </Stack>
                          </div>
                        )
                      } else {
                        return ""
                      }
                    })}
                  </Stack>
              </section>
            </Card>
            <Card variant="outlined" className={`${styles.section} ${styles.normalSection}`}>
              <section>
                <b>Progress section</b> - will contain the event log, notifications, buttons for making phase-specific decisions, and some indication of who we are waiting for and what we are waiting for them to do.
              </section>
            </Card>
          </div>
        </div>
      </main>
    </>
  )
}

export default PlayGamePage;

// The game is retrieved by the frontend server
export async function getServerSideProps(context: GetServerSidePropsContext) {

  // Get client cookie data from the page request
  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context)

  // Get game Id from the URL
  const gameId = context.params?.id

  // Asynchronously retrieve the game
  const gameResponse = await request('GET', `games/${gameId}/`, clientAccessToken, clientRefreshToken)

  // Track whether there has been an authentication failure due to bad credentials
  let authFailure = false

  // Ensure that the game response is OK before getting data
  let gameJSON = null
  if (gameResponse.status === 200) {
    gameJSON = gameResponse.data
  } else if (gameResponse.status === 401) {
    authFailure = true
  }

  return {
    props: {
      ssrEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
      clientTimezone: clientTimezone,
      gameId: gameId,
      authFailure: authFailure,
      initialGame: gameJSON
    }
  };
}
