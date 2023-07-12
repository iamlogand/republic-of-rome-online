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

import Game, { Participant } from '@/classes/Game';
import Breadcrumb from '@/components/Breadcrumb';
import PageError from '@/components/PageError';
import { useAuthContext } from '@/contexts/AuthContext';
import getInitialCookieData from '@/functions/cookies';
import formatDate from '@/functions/date';
import request, { ResponseType } from '@/functions/request';
import KeyValueList from '@/components/KeyValueList';
import { deserializeToInstance } from '@/functions/serialize';

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface GamePageProps {
  initialGame: string;
  gameId: string;
  clientTimezone: string;
}

const GamePage = (props: GamePageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext();
  const [game, setGame] = useState<Game | undefined>(() => {
    if (props.initialGame) {
      return deserializeToInstance<Game>(Game, props.initialGame);
    }
  });

  const gameWebSocketURL = webSocketURL + 'games/' + props.gameId + '/';
  const { sendMessage, lastMessage } = useWebSocket(gameWebSocketURL, {
    onOpen: () => console.log('WebSocket connection opened'),
    // Attempt to reconnect on all close events, such as server shutting down
    shouldReconnect: (closeEvent) => true,
  });

  const fetchGame = useCallback(async () => {
    const response = await request('GET', 'games/' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      setGame(deserializeToInstance<Game>(Game, response.data));
    } else {
      setGame(undefined);
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser]);

  useEffect(() => {
    if (lastMessage?.data == "status change") {
      fetchGame();
    }
  }, [lastMessage, fetchGame])

  const handleDelete = () => {
    const deleteGame = async () => {
      if (window.confirm(`Are you sure you want to permanently delete this game?`)) {
        const response = await request('DELETE', 'games/' + props.gameId + '/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
        if (response.status === 204) {
          router.push('/games/');
          sendMessage('status change');
        }
      }
    }
    deleteGame();
  }

  const handleJoin = () => {
    const joinGame = async () => {
      const data = { "game": props.gameId }
      const response = await request('POST', 'game-participants/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser, data);
      if (response.status == 201) {
        sendMessage('status change');
      }
    }
    joinGame();
  }


  const handleLeave = () => {
    const leaveGame = async () => {
      const id = game?.participants.find(participant => participant.username === user?.username)?.id;
      if (id !== null) {
        const response = await request('DELETE', 'game-participants/' + id, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
        if (response.status == 204) {
          sendMessage('status change');
        }
      }
    }
    leaveGame();
  }

  // `handleKick` is similar to `handleLeave`, except participant ID is passed as an argument,
  // so it could be another participant other than this user.
  const handleKick = (id: string) => {
    const kick = async () => {
      const response = await request('DELETE', 'game-participants/' + id, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
      if (response.status == 204) {
        sendMessage('status change');
      }
    }
    kick();
  }

  const handleStart = () => {
    const startGame = async () => {
      if (window.confirm(`Are you sure you want to start this game?`)) {
        const response = await request('POST', 'games/' + props.gameId + '/start-game/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
        if (response.status == 200) {
          sendMessage('status change');
          router.push('/games/' + props.gameId + '/play/');
        }
      }
    }
    startGame();
  }

  // Render page error if user is not signed in
  if (user === undefined) {
    return <PageError statusCode={401} />;
  } else if (game == undefined) {
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
            <Card style={{ flexGrow: 1 }}>
              <Card variant='outlined' style={{ height: "100%" }}>
                <h3 style={{ marginLeft: "16px", marginBottom: 0 }}>Details</h3>
                <div style={{ padding: "10px 0" }}>
                  <KeyValueList pairs={details} divider={true} />
                </div>
              </Card>
            </Card>
            <Card style={{ flexGrow: 1 }}>
              <Card variant='outlined' style={{ paddingBottom: "6px", height: "100%" }}>
                <div style={{ marginLeft: "16px", marginBottom: "6px" }}>
                  <h3>Participants</h3>
                  <p style={{ margin: 0 }}>{game.participants.length} of 6 spaces reserved</p>
                </div>
                <List>
                  {game.participants.sort((a: Participant, b: Participant) => {
                    // Sort the participants from first to last joined
                    return new Date(a.join_date).getTime() - new Date(b.join_date).getTime();
                  }).map((participant, index) => {

                    // Decide whether the player can be kicked by this user, if so make the button
                    const canKick = game.host === user.username && participant.username !== user.username;
                    const kickButton = canKick ? (
                      <IconButton edge="end" aria-label="delete" style={{ width: 40 }} onClick={() => handleKick(participant.id)}>
                        <FontAwesomeIcon icon={faXmark} width={14} height={14} />
                      </IconButton>
                    ) : "";

                    return (
                      <ListItem key={index}
                        secondaryAction={kickButton}
                      >
                        <ListItemAvatar>
                          <Avatar>{capitalize(participant.username.substring(0, 1))}</Avatar>
                        </ListItemAvatar>
                        <ListItemText>
                          <span><b>{participant.username} {participant.username == game.host && <span>(host)</span>}</b></span>
                        </ListItemText>
                      </ListItem>
                    )
                  })}
                </List>
                {game.participants.length < 3 &&
                  <div style={{ marginLeft: "16px", marginBottom: "6px" }}>
                    <p style={{ margin: 0 }}>You need at least {6 - game.participants.length - 3} more to start</p>
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
                    <Button variant="outlined" LinkComponent={Link} href={`/games/${game.id}/edit`}>
                      <FontAwesomeIcon icon={faEdit} style={{ marginRight: "8px" }} width={14} height={14} />
                      Edit
                    </Button>
                    {game.participants.length >= 3 && game.start_date === null &&
                      <Button variant="contained" color="success" onClick={handleStart}>
                        <FontAwesomeIcon icon={faPlay} style={{ marginRight: "8px" }} width={14} height={14} />
                        Start
                      </Button>
                    }
                  </>
                }
                {!game.participants.some(participant => participant.username === user.username) && game.participants.length < 6 &&
                  <Button variant="outlined" onClick={handleJoin}>
                    <FontAwesomeIcon icon={faCirclePlus} style={{ marginRight: "8px" }} width={14} height={14} />
                    Join
                  </Button>
                }
                {game.host !== user.username && game.participants.some(participant => participant.username === user.username) &&
                  <Button variant="outlined" onClick={handleLeave} color="warning">
                    Leave
                  </Button>
                }
                {game.start_date !== null && game.participants.length >= 3 &&
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

export default GamePage;

export async function getServerSideProps(context: GetServerSidePropsContext) {

  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context);

  const id = context.params?.id;
  const response = await request('GET', `games/${id}/`, clientAccessToken, clientRefreshToken);

  const game = JSON.stringify(deserializeToInstance<Game>(Game, response.data));

  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
      clientTimezone: clientTimezone,
      gameId: id,
      initialGame: game ?? null
    }
  };
}
