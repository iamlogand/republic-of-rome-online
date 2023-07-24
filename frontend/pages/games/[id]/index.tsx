import { useCallback, useEffect, useState } from 'react';
import { GetServerSidePropsContext } from 'next';
import router from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import useWebSocket from 'react-use-websocket';

import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Card from '@mui/material/Card';
import Avatar from '@mui/material/Avatar';
import { capitalize } from '@mui/material/utils';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCirclePlus, faTrash, faEdit, faXmark, faPlay } from '@fortawesome/free-solid-svg-icons';

import Game from '@/classes/Game';
import Breadcrumb from '@/components/Breadcrumb';
import PageError from '@/components/PageError';
import { useAuthContext } from '@/contexts/AuthContext';
import getInitialCookieData from '@/functions/cookies';
import formatDate from '@/functions/date';
import request, { ResponseType } from '@/functions/request';
import KeyValueList from '@/components/KeyValueList';
import { deserializeToInstance, deserializeToInstances } from '@/functions/serialize';
import GameParticipant from '@/classes/GameParticipant';
import User from '@/classes/User';

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface GameLobbyPageProps {
  clientTimezone: string
  gameID: string
  authFailure: boolean
  initialGame: string
  initialGameParticipants: string
  initialUsers: string
}

// The "Game Lobby" page component
const GameLobbyPage = (props: GameLobbyPageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext();

  const [game, setGame] = useState<Game | null>(() => {
    if (props.initialGame) {
      return deserializeToInstance<Game>(Game, props.initialGame);
    }
    return null
  });
  const [gameParticipants, setGameParticipants] = useState<GameParticipant[]>(() => {
    if (props.initialGameParticipants) {
      return deserializeToInstances<GameParticipant>(GameParticipant, props.initialGameParticipants)
    }
    return []
  });

  // Establish a WebSocket connection and provide a state containing the last message
  const gameWebSocketURL = webSocketURL + `games/${props.gameID}/`;
  const { lastMessage } = useWebSocket(gameWebSocketURL, {
    onOpen: () => console.log('WebSocket connection opened'),
    // Attempt to reconnect on all close events, such as server shutting down
    shouldReconnect: (closeEvent) => true,
  });

  // Fetch game, game participants and users
  const fetchGameAndPlayers = useCallback(async () => {
    // Fetch game and game participants
    const gameRequest = await request('GET', `games/${props.gameID}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    const gameParticipantsRequest = await request('GET', `game-participants/?game=${props.gameID}&prefetch_users`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    const [gameResponse, gameParticipantsResponse] = await Promise.all([gameRequest, gameParticipantsRequest])

    // Deserialize the game and game participants
    let newGame: Game | null = null
    let newGameParticipants: GameParticipant[] = []
    if (gameResponse.status === 200 && gameParticipantsResponse.status === 200) {
      newGame = deserializeToInstance<Game>(Game, gameResponse.data)
      newGameParticipants = deserializeToInstances<GameParticipant>(GameParticipant, gameParticipantsResponse.data)
    }

    // Set the game, game participants and users
    setGame(newGame)
    setGameParticipants(newGameParticipants)
  }, [props.gameID, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Fetch game, game participants and users on status change WebSocket message
  useEffect(() => {
    if (lastMessage?.data == "status change") {
      fetchGameAndPlayers()
    }
  }, [lastMessage, fetchGameAndPlayers])

  // Handle deletion of the game
  const handleDelete = () => {
    const deleteGame = async () => {
      if (window.confirm(`Are you sure you want to permanently delete this game?`)) {
        const response = await request('DELETE', `games/${props.gameID}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
        if (response.status === 204) {
          router.push('/games/');
        }
      }
    }
    deleteGame();
  }

  // Handle join game (create a game participant)
  const handleJoin = () => {
    const data = { "game": props.gameID }
    request('POST', 'game-participants/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser, data);
  }

  // Handle leave game (delete a game participant)
  const handleLeave = () => {
    if (gameParticipants && user) {
      const id = gameParticipants.find(participant => {
        if (participant.user instanceof User) {
          return participant.user.id.toString() === user.id.toString()
        } else {
          return participant.user.toString() === user.id.toString()
        }
      })?.id
      console.log(id)
      if (id !== null) {
        request('DELETE', `game-participants/${id}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser)
      }
    }
  }

  // `handleKick` is similar to `handleLeave`, except participant ID is passed as an argument,
  // so it could be another participant other than this user.
  const handleKick = (id: string) => {
    request('DELETE', `game-participants/${id}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
  }

  // Handle game start - this triggers start and setup of the game
  const handleStart = () => {
    if (window.confirm(`Are you sure you want to start this game?`)) {
      request('POST', `games/${props.gameID}/start-game/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    }
  }

  // Sign out if authentication failed on the server
  if (props.authFailure) {
    setAccessToken('')
    setRefreshToken('')
    setUser(null)
  }

  // Render page error if user is not signed in
  if (user === null || props.authFailure) {
    return <PageError statusCode={401} />;
  } else if (game?.id == null) {
    return <PageError statusCode={404} />
  }

  const getFormattedStartDate = () => {
    if (game.start_date && game.start_date instanceof Date) {
      return formatDate(game.start_date, props.clientTimezone)
    } else {
      return "";
    }
  }

  const details = [
    { key: "Host", value: game.host ?? '' },
    { key: "Creation Date", value: formatDate(game.creation_date, props.clientTimezone) },
    { key: "Start Date", value: getFormattedStartDate() }
  ]

  return (
    <>
      <Head>
        <title>{game ? `${game.name} (Lobby) | Republic of Rome Online` : 'Loading... | Republic of Rome Online'}</title>
      </Head>
      <main>

        <Breadcrumb customItems={[{ index: 2, text: game.name + " (Lobby)" }]} />

        <h2 id="page-title" style={{ marginBottom: 0 }}>{game.name}</h2>
        <h3 style={{ marginTop: 0, color: "var(--foreground-color-muted)" }}>Game Lobby</h3>
        {game.description && <p>{game.description}</p>}

        <Stack direction={{ xs: "column" }} gap={2}>
          <Stack direction={{ xs: "column", sm: "row" }} gap={{ xs: 2 }}>
            <Card sx={{ width: { xs: "100%", sm: "50%" } }}>
              <Card variant='outlined' style={{ height: "100%" }}>
                <h3 style={{ marginLeft: "16px", marginBottom: 0 }}>Details</h3>
                <div style={{ padding: "10px 0" }}>
                  <KeyValueList pairs={details} divider={true} />
                </div>
              </Card>
            </Card>
            <Card sx={{ width: { xs: "100%", sm: "50%" } }}>
              <Card variant='outlined' style={{ paddingBottom: "6px", height: "100%" }}>
                <div style={{ marginLeft: "16px", marginBottom: "6px" }}>
                  <h3>Participants</h3>
                  <p style={{ margin: 0 }}>{gameParticipants.length} of 6 spaces reserved</p>
                </div>
                <List>
                  {gameParticipants.sort((a: GameParticipant, b: GameParticipant) => {
                    // Sort the participants from first to last joined
                    return new Date(a.joinDate).getTime() - new Date(b.joinDate).getTime();
                  }).map((participant, index) => {

                    // Decide whether the player can be kicked by this user, if so make the button
                    let canKick = true

                    if (game.step > 0) canKick = false
                    if (game.host !== user.username) canKick = false
                    if (participant.user === user.id.toString()) canKick = false

                    const kickButton = canKick ? (
                      <IconButton edge="end" aria-label="delete" style={{ width: 40 }} onClick={() => handleKick(participant.id)}>
                        <FontAwesomeIcon icon={faXmark} width={14} height={14} />
                      </IconButton>
                    ) : "";

                    if (participant.user instanceof User) {
                      return (
                        <ListItem key={index}
                          secondaryAction={kickButton}
                        >
                          <ListItemAvatar>
                            <Avatar>{capitalize(participant.user.username.substring(0, 1))}</Avatar>
                          </ListItemAvatar>
                          <ListItemText>
                            <span><b>{participant.user.username} {participant.user.username == game.host && <span>(host)</span>}</b></span>
                          </ListItemText>
                        </ListItem>
                      )
                    } else {
                      return ''
                    }
                  })}
                </List>
                {gameParticipants.length < 3 &&
                  <div style={{ marginLeft: "16px", marginBottom: "6px" }}>
                    <p style={{ margin: 0 }}>You need at least {6 - gameParticipants.length - 3} more to start</p>
                  </div>
                }
              </Card>
            </Card>
          </Stack>
          <Card>
            <Card variant='outlined' style={{ padding: "16px" }}>
              <h3 style={{ marginTop: 0 }}>Actions</h3>
              <Stack spacing={2} direction={{ xs: "column", sm: "row" }}>
                {game.host === user.username &&
                  <>
                    <Button variant="outlined" color="error" onClick={handleDelete}>
                      <FontAwesomeIcon icon={faTrash} style={{ marginRight: "8px" }} width={14} height={14} />
                      Delete
                    </Button>
                    {game.step === 0 &&
                      <Button variant="outlined" LinkComponent={Link} href={`/games/${game.id}/edit`}>
                        <FontAwesomeIcon icon={faEdit} style={{ marginRight: "8px" }} width={14} height={14} />
                        Edit
                      </Button>
                    }
                    {gameParticipants.length >= 3 && game.step === 0 &&
                      <Button variant="contained" color="success" onClick={handleStart}>
                        <FontAwesomeIcon icon={faPlay} style={{ marginRight: "8px" }} width={14} height={14} />
                        Start
                      </Button>
                    }
                  </>
                }
                {!gameParticipants.some(p => p.user instanceof User && p.user.id === user.id) && gameParticipants.length < 6 && game.step === 0 &&
                  <Button variant="outlined" onClick={handleJoin}>
                    <FontAwesomeIcon icon={faCirclePlus} style={{ marginRight: "8px" }} width={14} height={14} />
                    Join
                  </Button>
                }
                {game.host !== user.username && gameParticipants.some(p => p.user instanceof User && p.user.id === user.id) && game.step === 0 &&
                  <Button variant="outlined" onClick={handleLeave} color="warning">
                    Leave
                  </Button>
                }
                {game.step !== 0 && gameParticipants.length >= 3 &&
                  <Button variant="contained" LinkComponent={Link} href={`/games/${game.id}/play`}>
                    <FontAwesomeIcon icon={faPlay} style={{ marginRight: "8px" }} width={14} height={14} />
                    Play
                  </Button>
                }
              </Stack>
            </Card>
          </Card>
        </Stack>
      </main>
    </>
  )
}

export default GameLobbyPage;

// The game, participants and users are retrieved by the frontend server
export async function getServerSideProps(context: GetServerSidePropsContext) {

  // Get client cookie data from the page request
  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context)

  // Get game ID from the URL
  const gameID = context.params?.id

  // Asynchronously retrieve the game and related game participants
  const gameRequest = request('GET', `games/${gameID}/`, clientAccessToken, clientRefreshToken)
  const gameParticipantsRequest = request('GET', `game-participants/?game=${gameID}&prefetch_users`, clientAccessToken, clientRefreshToken)
  const [gameResponse, gameParticipantsResponse] = await Promise.all([gameRequest, gameParticipantsRequest])

  // Track whether there has been an authentication failure due to bad credentials
  let authFailure = false

  // Ensure that game and participant responses are OK before getting data
  let gameJSON = null
  let gameParticipantsJSON = null
  if (gameResponse.status === 200 && gameParticipantsResponse.status === 200) {
    gameJSON = gameResponse.data;
    gameParticipantsJSON = gameParticipantsResponse.data;
  } else if (gameResponse.status === 401 || gameParticipantsResponse.status === 401) {
    authFailure = true
  }

  return {
    props: {
      ssrEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
      clientTimezone: clientTimezone,
      gameID: gameID,
      authFailure: authFailure,
      initialGame: gameJSON,
      initialGameParticipants: gameParticipantsJSON
    }
  };
}
