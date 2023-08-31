import { useCallback, useEffect, useRef, useState } from 'react'
import Head from 'next/head'
import useWebSocket from 'react-use-websocket'

import Card from '@mui/material/Card'
import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'

import { useGameContext } from '@/contexts/GameContext'
import Game from '@/classes/Game'
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import Senator from '@/classes/Senator'
import Title from '@/classes/Title'
import PageError from '@/components/PageError'
import request from '@/functions/request'
import { useAuthContext } from '@/contexts/AuthContext'
import { deserializeToInstance, deserializeToInstances } from '@/functions/serialize'
import Collection from '@/classes/Collection'
import styles from "./GamePage.module.css"
import SenatorsTab from '@/components/SenatorList'
import FactionsTab from '@/components/MainSection_FactionsTab'
import DetailSection from '@/components/DetailSection'
import Turn from '@/classes/Turn'
import Phase from '@/classes/Phase'
import Step from '@/classes/Step'
import MetaSection from '@/components/MetaSection'
import PotentialAction from '@/classes/PotentialAction'
import ProgressSection from '@/components/ProgressSection'

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

// Props are passed here from the `GamePageWrapper`
export interface GamePageProps {
  clientTimezone: string
  gameId: string
  authFailure: boolean
  initialGame: string
  initialLatestSteps: string
}

// The game page component - the most important component in the frontend project.
// This would be an actual page if it wasn't wrapped by `GamePageWrapper`, which supplies `GameContext`
const GamePage = (props: GamePageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext()
  const [syncingGameData, setSyncingGameData] = useState<boolean>(true)

  // Game-specific state
  const { game, setGame, latestStep, setLatestStep, setAllPlayers, setAllFactions, setAllSenators, setAllTitles } = useGameContext()
  const [latestTurn, setLatestTurn] = useState<Turn | null>(null)
  const [latestPhase, setLatestPhase] = useState<Phase | null>(null)
  const [potentialActions, setPotentialActions] = useState<Collection<PotentialAction>>(new Collection<PotentialAction>())

  // Set game-specific state using initial data
  useEffect(() => {
    setGame(props.initialGame ? deserializeToInstance<Game>(Game, props.initialGame) : null)
  }, [props.initialGame, setGame])
  useEffect(() => {
    setLatestStep(props.initialLatestSteps ? deserializeToInstances<Step>(Step, props.initialLatestSteps)[0] : null)
  }, [props.initialLatestSteps, setLatestStep])

  // UI selections
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

    // Attempt to reconnect on all close events, such as temporary break of internet connection
    shouldReconnect: (closeEvent) => true,
  });

  // Fetch the game
  const fetchGame = useCallback(async () => {
    const response = await request('GET', `games/${props.gameId}/?prefetch_user`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstance = deserializeToInstance<Game>(Game, response.data)
      setGame(deserializedInstance)
    }
  }, [props.gameId, setGame, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch game players
  const fetchPlayers = useCallback(async () => {
    const response = await request('GET', `game-players/?game=${props.gameId}&prefetch_user`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<Player>(Player, response.data)
      setAllPlayers(new Collection<Player>(deserializedInstances))
    } else {
      setAllPlayers(new Collection<Player>())
    }
  }, [props.gameId, setAllPlayers, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch factions
  const fetchFactions = useCallback(async () => {
    const response = await request('GET', `factions/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<Faction>(Faction, response.data)
      setAllFactions(new Collection<Faction>(deserializedInstances))
    } else {
      setAllFactions(new Collection<Faction>())
    }
  }, [props.gameId, setAllFactions, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch senators
  const fetchSenators = useCallback(async () => {
    const response = await request('GET', `senators/?game=${props.gameId}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<Senator>(Senator, response.data)
      setAllSenators(new Collection<Senator>(deserializedInstances))
    } else {
      setAllSenators(new Collection<Senator>())
    }
  }, [props.gameId, setAllSenators, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch titles
  const fetchTitles = useCallback(async () => {
    const response = await request('GET', `titles/?game=${props.gameId}&active`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<Title>(Title, response.data)
      setAllTitles(new Collection<Title>(deserializedInstances))
    } else {
      setAllTitles(new Collection<Title>())
    }
  }, [props.gameId, setAllTitles, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest turn
  const fetchLatestTurn = useCallback(async () => {
    const response = await request('GET', `turns/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Turn>(Turn, response.data[0])
      setLatestTurn(deserializedInstance)
    }
  }, [props.gameId, setLatestTurn, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest phase
  const fetchLatestPhase = useCallback(async () => {
    const response = await request('GET', `phases/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Phase>(Phase, response.data[0])
      setLatestPhase(deserializedInstance)
    }
  }, [props.gameId, setLatestPhase, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest step
  const fetchLatestStep = useCallback(async (): Promise<Step | null> => {
    const response = await request('GET', `steps/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Step>(Step, response.data[0])
      setLatestStep(deserializedInstance)
      return deserializedInstance
    }
    return null
  }, [props.gameId, setLatestStep, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch potential actions
  const fetchPotentialActions = useCallback(async (step: Step) => {
    const response = await request('GET', `potential-actions/?step=${step.id}`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstances = deserializeToInstances<PotentialAction>(PotentialAction, response.data)
      setPotentialActions(new Collection<PotentialAction>(deserializedInstances))
    } else {
      setPotentialActions(new Collection<PotentialAction>())
    }
  }, [setPotentialActions, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Read WebSocket messages and use payloads to update state
  useEffect(() => {
    if (lastMessage?.data) {
      const deserializedData = JSON.parse(lastMessage.data)
      for (const message of deserializedData) {

        // Latest turn updates
        if (message?.instance?.class === "turn") {
          // Update the latest turn
          if (message?.operation === "create") {
            const newInstance = deserializeToInstance<Turn>(Turn, message.instance.data)
            if (newInstance) {
              setLatestTurn(newInstance)
            }
          }
        }

        // Latest phase updates
        if (message?.instance?.class === "phase") {
          // Update the latest phase
          if (message?.operation === "create") {
            const newInstance = deserializeToInstance<Phase>(Phase, message.instance.data)
            if (newInstance) {
              setLatestPhase(newInstance)
            }
          }
        }

        // Latest step updates
        if (message?.instance?.class === "step") {
          // Update the latest step
          if (message?.operation === "create") {
            const newInstance = deserializeToInstance<Step>(Step, message.instance.data)
            if (newInstance) {
              setLatestStep(newInstance)
            }
          }
        }

        // Potential action updates
        if (message?.instance?.class === "potential_action") {

          // Add a potential action
          if (message?.operation === "create") {
            const newInstance = deserializeToInstance<PotentialAction>(PotentialAction, message.instance.data)
            // Before updating state, ensure that this instance has not already been added
            if (newInstance) {
              setPotentialActions(
                (existingInstances) => {
                  if (existingInstances.allIds.includes(newInstance.id)) {
                    return existingInstances
                  } else {
                    return new Collection<PotentialAction>([...existingInstances.asArray, newInstance])
                  }
                }
              )
            }
          }

          // Remove a potential action
          if (message?.operation === "destroy") {
            const idToRemove = message.instance.id
            setPotentialActions((potentialActions) => new Collection<PotentialAction>(potentialActions.asArray.filter(p => p.id !== idToRemove)))
          }
        }

        // Active title updates
        if (message?.instance?.class === "title") {

          // Add an active title
          if (message?.operation === "create") {
            const newInstance = deserializeToInstance<Title>(Title, message.instance.data)
            // Before updating state, ensure that this instance has not already been added
            if (newInstance) {
              setAllTitles(
                (existingInstances) => {
                  if (existingInstances.allIds.includes(newInstance.id)) {
                    return existingInstances
                  } else {
                    return new Collection<Title>([...existingInstances.asArray, newInstance])
                  }
                }
              )
            }
          }

          // Remove an active title
          if (message?.operation === "destroy") {
            const idToRemove = message.instance.id
            setAllTitles((titles) => new Collection<Title>(titles.asArray.filter(t => t.id !== idToRemove)))
          }
        }
      }
    }
  }, [lastMessage, game?.id, setLatestTurn, setLatestPhase, setLatestStep, setPotentialActions, setAllTitles])

  // Fully synchronize all game data
  const fullSync = useCallback(async () => {
    console.log("[Full Sync] started")
    const startTime = performance.now()

    setSyncingGameData(true)
    
    // Fetch game data
    const requestsBatch1 = [
      fetchLatestStep(),  // Step is positional, because it's used in the next batch of requests
      fetchGame(),
      fetchPlayers(),
      fetchFactions(),
      fetchSenators(),
      fetchTitles(),
      fetchLatestTurn(),
      fetchLatestPhase()
    ]
    const results = await Promise.all(requestsBatch1)
    const updatedLatestStep = results[0]

    if (updatedLatestStep) {
      const requestsBatch2 = [
        fetchPotentialActions(updatedLatestStep)
      ]
      await Promise.all(requestsBatch2)
    }

    setSyncingGameData(false)

    // Track time taken to sync
    const endTime = performance.now()
    const timeTaken = Math.round(endTime - startTime)

    console.log(`[Full Sync] completed in ${timeTaken}ms`)
  }, [fetchGame, fetchPlayers, fetchFactions, fetchSenators, fetchTitles, fetchLatestTurn, fetchLatestPhase, fetchLatestStep, fetchPotentialActions])

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
      <main className={`${styles.playPage} ${styles.play}`}>
        {syncingGameData ? <div className={styles.loading}><span>Synchronizing: {game.name}</span><CircularProgress /></div>:
          <div className={styles.layout}>
            <Card variant="outlined" className={`${styles.section} ${styles.metaSection}`}>
              <MetaSection latestTurn={latestTurn} latestPhase={latestPhase} />
            </Card>
            <div className={styles.sections}>
              <Card variant="outlined" className={styles.normalSection}>
                <DetailSection />
              </Card>
              <Card variant="outlined" className={`${styles.normalSection} ${styles.mainSection}`}>
                <section className={styles.sectionContent}>
                  <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={mainTab} onChange={handleMainTabChange} className={styles.tabs}>
                      <Tab label="Factions" />
                      <Tab label="Senators" />
                    </Tabs>
                  </Box>
                  {mainTab === 0 && <FactionsTab />}
                  {mainTab === 1 && <SenatorsTab margin={8} selectable />}
                </section>
              </Card>
              <Card variant="outlined" className={styles.normalSection}>
                <ProgressSection allPotentialActions={potentialActions} />
              </Card>
            </div>
          </div>
        }
      </main>
    </>
  )
}

export default GamePage
