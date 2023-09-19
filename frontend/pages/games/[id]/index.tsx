import { useCallback, useEffect, useRef, useState } from 'react'
import { GetServerSidePropsContext } from 'next'
import router from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import useWebSocket from 'react-use-websocket'

import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Card from '@mui/material/Card'
import Avatar from '@mui/material/Avatar'
import { capitalize } from '@mui/material/utils'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemAvatar from '@mui/material/ListItemAvatar'
import ListItemText from '@mui/material/ListItemText'
import IconButton from '@mui/material/IconButton'
import Skeleton from '@mui/material/Skeleton'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCirclePlus, faTrash, faEdit, faXmark, faPlay, faEye } from '@fortawesome/free-solid-svg-icons'

import Game from '@/classes/Game'
import Breadcrumb from '@/components/Breadcrumb'
import PageError from '@/components/PageError'
import { useAuthContext } from '@/contexts/AuthContext'
import getInitialCookieData from '@/functions/cookies'
import formatDate from '@/functions/date'
import request from '@/functions/request'
import KeyValueList from '@/components/KeyValueList'
import { deserializeToInstance, deserializeToInstances } from '@/functions/serialize'
import Player from '@/classes/Player'
import User from '@/classes/User'
import Turn from '@/classes/Turn'
import Phase from '@/classes/Phase'
import Step from '@/classes/Step'
import styles from './index.module.css'

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? ""

interface GameLobbyPageProps {
  clientTimezone: string
  gameId: string
  authFailure: boolean
  initialGame: string
  initialUsers: string
}

// The "Game Lobby" page component
const GameLobbyPage = (props: GameLobbyPageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext()
  const [loading, setLoading] = useState<boolean>(true)

  // Game-specific state
  const [game, setGame] = useState<Game | null>(() => props.initialGame ? deserializeToInstance<Game>(Game, props.initialGame) : null)
  const [players, setPlayers] = useState<Player[]>([])
  const [latestTurn, setLatestTurn] = useState<Turn | null>(null)
  const [latestPhase, setLatestPhase] = useState<Phase | null>(null)
  const [latestStep, setLatestStep] = useState<Step | null>(null)

  // Establish a WebSocket connection and provide a state containing the last message
  const { lastMessage } = useWebSocket(webSocketURL + `games/${props.gameId}/?token=${accessToken}`, {
    
    // On connection open perform a full sync
    onOpen: () => {
      console.log('WebSocket connection opened')
      fullSync()
    },

    // On connection close perform a fetch to authenticate
    // This will sign the user out if the request fails, preventing the WebSocket from repeatedly trying to connect
    onClose: () => {
      console.log('WebSocket connection closed')
      fetchGame()
    },

    // Don't attempt to reconnect
    shouldReconnect: () => user ? true : false,
  })

  // Fetch the game
  const fetchGame = useCallback(async () => {
    const response = await request('GET', `games/${props.gameId}/?prefetch_user`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      const deserializedInstance = deserializeToInstance<Game>(Game, response.data)
      setGame(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch game players
  const fetchPlayers = useCallback(async () => {
    const playersResponse = await request('GET', `players/?game=${props.gameId}&prefetch_user`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (playersResponse.status === 200) {
      const newPlayers = deserializeToInstances<Player>(Player, playersResponse.data)
      setPlayers(newPlayers)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest turn
  const fetchLatestTurn = useCallback(async () => {
    const response = await request('GET', `turns/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Turn>(Turn, response.data[0])
      setLatestTurn(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest phase
  const fetchLatestPhase = useCallback(async () => {
    const response = await request('GET', `phases/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Phase>(Phase, response.data[0])
      setLatestPhase(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch the latest step
  const fetchLatestStep = useCallback(async () => {
    const response = await request('GET', `steps/?game=${props.gameId}&ordering=-index&limit=1`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200 && response.data.length > 0) {
      const deserializedInstance = deserializeToInstance<Step>(Step, response.data[0])
      setLatestStep(deserializedInstance)
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fully synchronize all game data
  const fullSync = useCallback(async () => {
    if (user === null) return  // Don't attempt to sync if user is not signed in

    console.log("[Full Sync] started")
    const startTime = performance.now()

    // Fetch game data
    setLoading(true)
    const gameResult = fetchGame()
    const playersResult = fetchPlayers()
    const latestTurnResult = fetchLatestTurn()
    const latestPhaseResult = fetchLatestPhase()
    const latestStepResult = fetchLatestStep()
    await Promise.all([gameResult, playersResult, latestTurnResult, latestPhaseResult, latestStepResult])
    setLoading(false)

    // Track time taken to sync
    const endTime = performance.now()
    const timeTaken = Math.round(endTime - startTime)

    console.log(`[Full Sync] completed in ${timeTaken}ms`)
  }, [fetchGame, fetchPlayers, fetchLatestTurn, fetchLatestPhase, fetchLatestStep])

  // Game players ref used in the "Read WebSocket messages" useEffect to
  // prevent players from having to be included in it's dependency array
  const playersRef = useRef(players);
  useEffect(() => {
    playersRef.current = players;
  }, [players]);

  // Read WebSocket messages and use payloads to update state
  useEffect(() => {
    if (lastMessage?.data) {
      const deserializedData = JSON.parse(lastMessage.data)
      if (deserializedData && deserializedData.length > 0) {
        for (const message of deserializedData) {

          // Game updates
          if (message?.instance?.class === "game") {
            // Update the game
            if (message?.operation === "update") {
              const updatedGame = deserializeToInstance<Game>(Game, message.instance.data)
              if (updatedGame) {
                setGame(updatedGame)
              }
            }
            // Delete the game
            if (message?.operation === "destroy") {
              const idToRemove = message.instance.id
              if (idToRemove === game?.id) {
                setGame(null)
              }
            }
          }

          // Game player updates
          if (message?.instance?.class === "player") {
            if (message?.operation === "create") {
              // Add a game player
              const newPlayer = deserializeToInstance<Player>(Player, message.instance.data)
              // Before updating state, ensure that this game player has not already been added
              if (newPlayer && !playersRef.current.some(p => p.id === newPlayer.id)) {
                setPlayers((players) => [...players, newPlayer])
              }
            } else if (message?.operation === "destroy") {
              // Remove a game player
              const idToRemove = message.instance.id
              setPlayers((players) => players.filter(p => p.id !== idToRemove))
            }
          }

          // Latest turn updates
          if (message?.instance?.class === "turn") {
            // Update the latest turn
            if (message?.operation === "create") {
              const updatedTurn = deserializeToInstance<Turn>(Turn, message.instance.data)
              if (updatedTurn) {
                setLatestTurn(updatedTurn)
              }
            }
          }

          // Latest phase updates
          if (message?.instance?.class === "phase") {
            // Update the latest phase
            if (message?.operation === "create") {
              const updatedPhase = deserializeToInstance<Phase>(Phase, message.instance.data)
              if (updatedPhase) {
                setLatestPhase(updatedPhase)
              }
            }
          }

          // Latest step updates
          if (message?.instance?.class === "step") {
            // Update the latest step
            if (message?.operation === "create") {
              const updatedStep = deserializeToInstance<Step>(Step, message.instance.data)
              if (updatedStep) {
                setLatestStep(updatedStep)
              }
            }
          }
        }
      }
    }
  }, [lastMessage, game?.id])

  // Handle deletion of the game
  const handleDelete = () => {
    const deleteGame = async () => {
      if (window.confirm(`Are you sure you want to permanently delete this game?`)) {
        const response = await request('DELETE', `games/${props.gameId}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
        if (response.status === 204) {
          router.push('/games/');
        }
      }
    }
    deleteGame();
  }

  // Handle join game (create a game player)
  const handleJoin = () => {
    const data = { "game": props.gameId }
    request('POST', 'players/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser, data);
  }

  // Handle leave game (delete a game player)
  const handleLeave = () => {
    if (players && user) {
      const id = players.find(player => player.user?.id === user.id)?.id
      if (id !== null) {
        request('DELETE', `players/${id}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
      }
    }
  }

  // `handleKick` is similar to `handleLeave`, except player Id is passed as an argument,
  // so it could be another player other than this user.
  const handleKick = (id: number) => {
    request('DELETE', `players/${id}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
  }

  // Handle game start - this triggers start and setup of the game
  const handleStart = () => {
    if (window.confirm(`Are you sure you want to start this game?`)) {
      request('POST', `games/${props.gameId}/start-game/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    }
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
  } else if (game === null) {
    return <PageError statusCode={404} />
  }

  const getFormattedStartDate = () => {
    if (game.start_date && game.start_date instanceof Date) {
      return formatDate(game.start_date, props.clientTimezone)
    } else {
      return "";
    }
  }

  // Build the game details list
  const overview = [
    { key: "Host", value: game.host?.username ?? '' }
  ]
  if (!loading) {
    if (latestTurn && latestPhase) {
      overview.push({ key: "Start Date", value: getFormattedStartDate() })
      overview.push({ key: "Progress", value: `Turn ${latestTurn.index}, ${latestPhase.name} Phase` })
    }
    else {
      overview.push({ key: "Creation Date", value: formatDate(game.creation_date, props.clientTimezone) })
      overview.push({ key: "Progress", value: `Not started` })
    }
  }

  return (
    <>
      <Head>
        <title>{game ? `${game.name} (Lobby) | Republic of Rome Online` : 'Loading... | Republic of Rome Online'}</title>
      </Head>
      <main className="standard-page">

        <Breadcrumb customItems={[{ index: 2, text: game.name + " (Lobby)" }]} />

        <h2 id="page-title" style={{ marginBottom: 0 }}>{game.name}</h2>
        <h3 style={{ marginTop: 0, color: "var(--foreground-color-muted)" }}>Game Lobby</h3>
        {game.description && <p>{game.description}</p>}

        <Stack direction={{ xs: "column" }} gap={2}>
          <Stack direction={{ xs: "column", sm: "row" }} gap={{ xs: 2 }}>
            <Card sx={{ width: { xs: "100%", sm: "50%" } }}>
              <Card variant='outlined' style={{ height: "100%" }}>
                <h3 style={{ marginLeft: "16px", marginBottom: 0 }}>Overview</h3>
                <div style={{ padding: "10px 0" }}>
                  { loading ?
                    <KeyValueList pairs={overview} divider={true} skeletonItems={2} />
                    :
                    <KeyValueList pairs={overview} divider={true} />
                  }
                </div>
              </Card>
            </Card>
            <Card sx={{ width: { xs: "100%", sm: "50%" } }}>
              <Card variant='outlined' style={{ paddingBottom: "6px", height: "100%" }}>
                <div style={{ marginLeft: 16, marginBottom: 6, marginRight: 16 }}>
                  <h3>Players</h3>
                  { !loading ?
                    <p style={{ margin: 0 }}>{players.length} of 6 spaces reserved</p>
                  :
                    <Skeleton variant="rounded" sx={{ height: "22px", width: "165px" }} />
                  }
                </div>
                { !loading ? <>
                  <List>
                    {players.sort((a: Player, b: Player) => {
                      // Sort the players from first to last joined
                      return new Date(a.joinDate).getTime() - new Date(b.joinDate).getTime();
                    }).map((player, index) => {

                      // Decide whether the player can be kicked by this user, if so make the button
                      let canKick = true

                      if (latestStep) canKick = false
                      if (game.host?.id === player.user?.id) canKick = false
                      if (game.host?.id !== user.id) canKick = false
                      if (player.user?.id === user.id) canKick = false

                      const kickButton = canKick ? (
                        <IconButton edge="end" aria-label="delete" style={{ width: 40 }} onClick={() => handleKick(player.id)}>
                          <FontAwesomeIcon icon={faXmark} width={14} height={14} />
                        </IconButton>
                      ) : "";

                      if (player.user instanceof User) {
                        return (
                          <ListItem key={index}
                            secondaryAction={kickButton}
                          >
                            <ListItemAvatar>
                              <Avatar>{capitalize(player.user.username.substring(0, 1))}</Avatar>
                            </ListItemAvatar>
                            <ListItemText>
                              <span><b>{player.user.username} {player.user.id === game.host?.id && <span>(host)</span>}</b></span>
                            </ListItemText>
                          </ListItem>
                        )
                      } else {
                        return ''
                      }
                    })}
                  </List>
                  {players.length < 3 &&
                    <div style={{ marginLeft: 16, marginBottom: 6 }}>
                      <p style={{ margin: 0 }}>You need at least {6 - players.length - 3} more to start</p>
                    </div>
                  }
                </>
                :
                <div className={styles.skeletonList}>
                  <div>
                    <Skeleton variant="circular" width={40} height={40} />
                    <Skeleton variant="text" sx={{ width: 100 }} />
                  </div>
                  <div>
                    <Skeleton variant="circular" width={40} height={40} />
                    <Skeleton variant="text" sx={{ width: 120 }} />
                  </div>
                  <div>
                    <Skeleton variant="circular" width={40} height={40} />
                    <Skeleton variant="text" sx={{ width: 80 }} />
                  </div>
                </div>}
              </Card>
            </Card>
          </Stack>
          { !loading &&
            <Card>
              <Card variant='outlined' style={{ padding: "16px" }}>
                <h3 style={{ marginTop: 0 }}>Actions</h3>
                <Stack spacing={2} direction={{ xs: "column", sm: "row" }}>
                  {game.host?.id === user.id &&
                    <>
                      <Button variant="outlined" color="error" onClick={handleDelete}>
                        <FontAwesomeIcon icon={faTrash} style={{ marginRight: "8px" }} width={14} height={14} />
                        Delete
                      </Button>
                      {!latestStep &&
                        <Button variant="outlined" LinkComponent={Link} href={`/games/${game.id}/edit`}>
                          <FontAwesomeIcon icon={faEdit} style={{ marginRight: "8px" }} width={14} height={14} />
                          Edit
                        </Button>
                      }
                      {players.length >= 3 && !latestStep &&
                        <Button variant="contained" color="success" onClick={handleStart}>
                          <FontAwesomeIcon icon={faPlay} style={{ marginRight: "8px" }} width={14} height={14} />
                          Start
                        </Button>
                      }
                    </>
                  }
                  {!players.some(p => p.user instanceof User && p.user.id === user.id) && players.length < 6 && !latestStep &&
                    <Button variant="outlined" onClick={handleJoin}>
                      <FontAwesomeIcon icon={faCirclePlus} style={{ marginRight: "8px" }} width={14} height={14} />
                      Join
                    </Button>
                  }
                  {game.host?.id !== user.id && players.some(p => p.user instanceof User && p.user.id === user.id) && !latestStep &&
                    <Button variant="outlined" onClick={handleLeave} color="warning">
                      Leave
                    </Button>
                  }
                  {latestStep &&
                    <Button variant="contained" LinkComponent={Link} href={`/games/${game.id}/play`}>
                      
                      {players.some(p => p.user instanceof User && p.user.id === user.id) ?
                        <>
                          <FontAwesomeIcon icon={faPlay} style={{ marginRight: "8px" }} width={14} height={14} />
                          Play
                        </>
                        :
                        <>
                          <FontAwesomeIcon icon={faEye} style={{ marginRight: "8px" }} width={14} height={14} />
                          Spectate
                        </>
                      }
                    </Button>
                  }
                </Stack>
              </Card>
            </Card>
          }
        </Stack>
      </main>
    </>
  )
}

export default GameLobbyPage;

// The game is retrieved by the frontend server
export async function getServerSideProps(context: GetServerSidePropsContext) {

  // Get client cookie data from the page request
  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context)

  // Get game Id from the URL
  const gameId = context.params?.id

  // Asynchronously retrieve the game
  const gameResponse = await request('GET', `games/${gameId}/?prefetch_user`, clientAccessToken, clientRefreshToken)

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
