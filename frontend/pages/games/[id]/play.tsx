import { useCallback, useEffect, useState } from 'react'
import Head from 'next/head'
import { GetServerSidePropsContext } from 'next'
import useWebSocket from 'react-use-websocket'

import Card from '@mui/material/Card'
import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import Box from '@mui/material/Box'

import Game from '@/classes/Game'
import GameParticipant from '@/classes/GameParticipant'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import Office from '@/classes/Office'
import PageError from '@/components/PageError'
import getInitialCookieData from '@/functions/cookies'
import request from '@/functions/request'
import { useAuthContext } from '@/contexts/AuthContext'
import { deserializeToInstance, deserializeToInstances } from '@/functions/serialize'
import Collection from '@/classes/Collection'
import styles from "./play.module.css"
import SenatorsTab from '@/components/MainTab_Senators'
import FactionsTab from '@/components/MainTab_FactionsTab'
import DetailSection from '@/components/DetailSection'
import Step from '@/classes/Step'

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface PlayGamePageProps {
  clientTimezone: string
  gameId: string
  authFailure: boolean
  initialGame: string
}

// The "Play Game" page component
const PlayGamePage = (props: PlayGamePageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext()

  // Game-specific state
  const [game, setGame] = useState<Game | null>(() =>
    props.initialGame ? deserializeToInstance<Game>(Game, props.initialGame) : null
  )
  const [gameParticipants, setGameParticipants] = useState<Collection<GameParticipant>>(new Collection<GameParticipant>())
  const [factions, setFactions] = useState<Collection<Faction>>(new Collection<Faction>())
  const [senators, setSenators] = useState<Collection<FamilySenator>>(new Collection<FamilySenator>())
  const [offices, setOffices] = useState<Collection<Office>>(new Collection<Office>())
  const [latestStep, setLatestStep] = useState<Step | null>(null)

  // UI selections
  const [selectedEntity, setSelectedEntity] = useState<SelectedEntity | null>(null)
  const [mainTab, setMainTab] = useState(0);

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

  // Fetch senators
  const fetchSenators = useCallback(async () => {
    const response = await request('GET', `family-senators/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<FamilySenator>(FamilySenator, response.data)
      setSenators(new Collection<FamilySenator>(deserializedInstances));
    } else {
      setSenators(new Collection<FamilySenator>());
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch offices
  const fetchOffices = useCallback(async () => {
    const response = await request('GET', `offices/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<Office>(Office, response.data)
      setOffices(new Collection<Office>(deserializedInstances));
    } else {
      setOffices(new Collection<Office>());
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest step
  const fetchLatestStep = useCallback(async () => {
    const response = await request('GET', `steps/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Step>(Step, response.data[0])
      setLatestStep(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch game participants, factions and senators once on initial render
  useEffect(() => {
    fetchGameParticipants()
    fetchFactions()
    fetchSenators()
    fetchOffices()
    fetchLatestStep()
  }, [fetchGameParticipants, fetchFactions, fetchSenators, fetchOffices, fetchLatestStep])

  const handleMainTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setMainTab(newValue)
  }
  
  // Render page error if user is not signed in
  if (user === null || props.authFailure) {
    return <PageError statusCode={401} />;
  } else if (game === null || !latestStep) {
    return <PageError statusCode={404} />
  }

  return (
    <>
      <Head>
        <title>{game ? `${game.name} | Republic of Rome Online` : 'Loading... | Republic of Rome Online'}</title>
      </Head>
      <main className={styles.playPage}>
        <div className={styles.layout}>
          <Card variant="outlined" className={`${styles.section} ${styles.metaSection}`}>
            <section style={{padding: 8}}>
              <b>Meta section</b> - will contain turn number, phase, state treasury and some info about your faction (like color, vote count, total influence, faction treasury) 
            </section>
          </Card>
          <div className={styles.sections}>
            <Card variant="outlined" className={styles.normalSection}>
              <DetailSection gameParticipants={gameParticipants} factions={factions} senators={senators} offices={offices} selectedEntity={selectedEntity} setSelectedEntity={setSelectedEntity} />
            </Card>
            <Card variant="outlined" className={`${styles.normalSection} ${styles.mainSection}`}>
              <section className={styles.sectionContent}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                  <Tabs value={mainTab} onChange={handleMainTabChange} className={styles.tabs}>
                    <Tab label="Factions" />
                    <Tab label="Senators" />
                  </Tabs>
                </Box>
                {mainTab === 0 && <FactionsTab gameParticipants={gameParticipants} factions={factions} senators={senators} offices={offices} setSelectedEntity={setSelectedEntity} />}
                {mainTab === 1 && <SenatorsTab gameParticipants={gameParticipants} factions={factions} senators={senators} offices={offices} setSelectedEntity={setSelectedEntity} />}
              </section>
            </Card>
            <Card variant="outlined" className={styles.normalSection}>
              <section style={{padding: 8}}>
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
