import { useCallback, useEffect, useState } from 'react'
import Head from 'next/head'
import { GetServerSidePropsContext } from 'next'
import useWebSocket from 'react-use-websocket'

import Card from '@mui/material/Card'
import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'

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
import Turn from '@/classes/Turn'
import Phase from '@/classes/Phase'
import Step from '@/classes/Step'
import MetaSection from '@/components/MetaSection'
import PotentialAction from '@/classes/PotentialAction'
import ProgressSection from '@/components/ProgressSection'
import SelectedEntity from "@/types/selectedEntity"

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface PlayGamePageProps {
  clientTimezone: string
  gameId: string
  authFailure: boolean
  initialGame: string
  initialLatestSteps: string
}

// The "Play Game" page component
const PlayGamePage = (props: PlayGamePageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext()
  const [syncingGameData, setSyncingGameData] = useState<boolean>(true)

  // Game-specific state
  const [game, setGame] = useState<Game | null>(() =>
    props.initialGame ? deserializeToInstance<Game>(Game, props.initialGame) : null
  )
  const [gameParticipants, setGameParticipants] = useState<Collection<GameParticipant>>(new Collection<GameParticipant>())
  const [factions, setFactions] = useState<Collection<Faction>>(new Collection<Faction>())
  const [senators, setSenators] = useState<Collection<FamilySenator>>(new Collection<FamilySenator>())
  const [offices, setOffices] = useState<Collection<Office>>(new Collection<Office>())
  const [latestTurn, setLatestTurn] = useState<Turn | null>(null)
  const [latestPhase, setLatestPhase] = useState<Phase | null>(null)
  const [latestStep, setLatestStep] = useState<Step | null>(() =>
    props.initialLatestSteps ? deserializeToInstances<Step>(Step, props.initialLatestSteps)[0] : null
  )
  const [potentialActions, setPotentialActions] = useState<Collection<PotentialAction>>(new Collection<PotentialAction>())

  // UI selections
  const [selectedEntity, setSelectedEntity] = useState<SelectedEntity | null>(null)
  const [mainTab, setMainTab] = useState(0);

  // Establish a WebSocket connection and provide a state containing the last message
  const { lastMessage } = useWebSocket(webSocketURL + `games/${props.gameId}/`, {

    // On connection open, if this isn't the first render then perform a full sync
    onOpen: () => {
      console.log('WebSocket connection opened')
      fullSync()
    },

    // On connection close, only write a message to the console
    onClose: () => console.log('WebSocket connection closed'),

    // Attempt to reconnect on all close events, such as server shutting down
    shouldReconnect: (closeEvent) => true,
  });

  // Fetch the game
  const fetchGame = useCallback(async () => {
    const response = await request('GET', `games/${props.gameId}/?prefetch_user`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstance = deserializeToInstance<Game>(Game, response.data)
      setGame(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch game participants
  const fetchGameParticipants = useCallback(async () => {
    const response = await request('GET', `game-participants/?game=${props.gameId}&prefetch_user`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<GameParticipant>(GameParticipant, response.data)
      setGameParticipants(new Collection<GameParticipant>(deserializedInstances))
    } else {
      setGameParticipants(new Collection<GameParticipant>())
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch factions
  const fetchFactions = useCallback(async () => {
    const response = await request('GET', `factions/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<Faction>(Faction, response.data)
      setFactions(new Collection<Faction>(deserializedInstances))
    } else {
      setFactions(new Collection<Faction>())
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch senators
  const fetchSenators = useCallback(async () => {
    const response = await request('GET', `family-senators/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<FamilySenator>(FamilySenator, response.data)
      setSenators(new Collection<FamilySenator>(deserializedInstances))
    } else {
      setSenators(new Collection<FamilySenator>())
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch offices
  const fetchOffices = useCallback(async () => {
    const response = await request('GET', `offices/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<Office>(Office, response.data)
      setOffices(new Collection<Office>(deserializedInstances))
    } else {
      setOffices(new Collection<Office>())
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest turn
  const fetchLatestTurn = useCallback(async () => {
    const response = await request('GET', `turns/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Turn>(Turn, response.data[0])
      setLatestTurn(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest phase
  const fetchLatestPhase = useCallback(async () => {
    const response = await request('GET', `phases/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Phase>(Phase, response.data[0])
      setLatestPhase(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest step
  const fetchLatestStep = useCallback(async () => {
    const response = await request('GET', `steps/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Step>(Step, response.data[0])
      setLatestStep(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch potential actions
  const fetchPotentialActions = useCallback(async () => {
    const response = await request('GET', `potential-actions/?step=${latestStep?.id}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstances = deserializeToInstances<PotentialAction>(PotentialAction, response.data)
      setPotentialActions(new Collection<PotentialAction>(deserializedInstances))
    } else {
      setPotentialActions(new Collection<PotentialAction>())
    }
  }, [latestStep?.id, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fully synchronize all game data
  const fullSync = useCallback(async () => {
    console.log("[Full Sync] started")
    const startTime = performance.now()

    setSyncingGameData(true)
    
    // Fetch game data
    const requests = [
      fetchGame(),
      fetchGameParticipants(),
      fetchFactions(),
      fetchSenators(),
      fetchOffices(),
      fetchLatestTurn(),
      fetchLatestPhase(),
      fetchLatestStep(),
      fetchPotentialActions()
    ];
    await Promise.all(requests)

    setSyncingGameData(false)

    // Track time taken to sync
    const endTime = performance.now()
    const timeTaken = Math.round(endTime - startTime)

    console.log(`[Full Sync] completed in ${timeTaken}ms`)
  }, [fetchGame, fetchGameParticipants, fetchFactions, fetchSenators, fetchOffices, fetchLatestTurn, fetchLatestPhase, fetchLatestStep, fetchPotentialActions])

  const handleMainTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setMainTab(newValue)
  }

  // Sign out if authentication failed on the server
  useEffect(() => {
    if (props.authFailure) {
      setAccessToken('')
      setRefreshToken('')
      setUser(null)
    }
  }, [props.authFailure, setAccessToken, setRefreshToken, setUser])
  
  // Render page error if user is not signed in
  if (user === null || props.authFailure) {
    return <PageError statusCode={401} />;
  } else if (game === null || game.start_date === null) {
    // Start date is used to work out whether the game has started before the latest step is received.
    return <PageError statusCode={404} />
  }

  return (
    <>
      <Head>
        <title>{game ? `${game.name} | Republic of Rome Online` : 'Loading... | Republic of Rome Online'}</title>
      </Head>
      <main className={styles.playPage}>
        {syncingGameData ? <div className={styles.loading}><span>Synchronizing: {game.name}</span><CircularProgress /></div>:
          <div className={styles.layout}>
            <Card variant="outlined" className={`${styles.section} ${styles.metaSection}`}>
              <MetaSection game={game} latestTurn={latestTurn} latestPhase={latestPhase} latestStep={latestStep} />
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
                <ProgressSection gameParticipants={gameParticipants} factions={factions} potentialActions={potentialActions} setSelectedEntity={setSelectedEntity} />
              </Card>
            </div>
          </div>
        }
      </main>
    </>
  )
}

export default PlayGamePage

// The game is retrieved by the frontend server
export async function getServerSideProps(context: GetServerSidePropsContext) {

  // Get client cookie data from the page request
  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context)

  // Get game Id from the URL
  const gameId = context.params?.id

  // Asynchronously retrieve the game and latest step
  const requests = [
    request('GET', `games/${gameId}/`, clientAccessToken, clientRefreshToken),
    request('GET', `steps/?game=${gameId}&ordering=-index&limit=1`, clientAccessToken, clientRefreshToken)
  ]
  const [gameResponse, stepsResponse] = await Promise.all(requests)

  // Track whether there has been an authentication failure due to bad credentials
  let authFailure = false

  // Ensure that the responses are OK before getting data
  let gameJSON = null
  let stepsJSON = null
  if (gameResponse.status === 200 && stepsResponse.status === 200) {
    gameJSON = gameResponse.data
    stepsJSON = stepsResponse.data
  } else if (gameResponse.status === 401 || stepsResponse.status === 401) {
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
      initialGame: gameJSON,
      initialLatestSteps: stepsJSON
    }
  };
}
