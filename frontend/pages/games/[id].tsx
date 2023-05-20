import { useEffect, useState } from 'react';
import { GetServerSidePropsContext } from 'next';
import router from 'next/router';
import Head from 'next/head';

import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Card from '@mui/material/Card';
import Avatar from '@mui/material/Avatar';
import { capitalize } from '@mui/material/utils';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCirclePlus, faTrash } from '@fortawesome/free-solid-svg-icons';

import Game from '@/classes/Game';
import Breadcrumb from '@/components/Breadcrumb';
import PageError from '@/components/PageError';
import { useAuthContext } from '@/contexts/AuthContext';
import getInitialCookieData from '@/functions/cookies';
import formatDate from '@/functions/date';
import request, { ResponseType } from '@/functions/request';
import KeyValueList from '@/components/KeyValueList';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';

interface GamePageProps {
  initialGame: string;
  gameId: string;
  clientTimezone: string;
}

const GamePage = (props: GamePageProps) => {
  const { username, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const [game, setGame] = useState<Game | undefined>(() => {
    if (props.initialGame) {
      const gameObject = JSON.parse(props.initialGame);
      if (gameObject.name) {  // Might be invalid data, so check for name property
        return new Game(gameObject);
      }
    }
  });

  useEffect(() => {
    const fetchData = async () => {
      const response = await request('GET', 'games/' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
      if (response.status === 200) {
        const game = getGame(response);
        if (game) {
          setGame(game);
        }
      }
    }
    fetchData();
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername])

  const handleDelete = () => {
    const deleteGame = async () => {
      const response = await request('DELETE', 'games/' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
      if (response.status === 204) {
        router.push('/games/');
      }
    }
    deleteGame();
  }

  const handleJoin = () => {
    const joinGame = async () => {
      const data = { "game": props.gameId }
      const response = await request('POST', 'game_participants/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername, data);
      if (response.status === 204) {
        router.push('/games/');
      }
    }
    joinGame();
  }

  // Render page error if user is not signed in
  if (username === '') {
    return <PageError statusCode={401} />;
  } else if (game == null) {
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
    { key: "Host", value: game.owner ?? ''},
    { key: "Creation Date", value: formatDate(game.creation_date, props.clientTimezone) },
    { key: "Start Date", value: getFormattedStartDate() }
  ]

  return (
    <>
      <Head>
        <title>Game Lobby - Republic of Rome Online</title>
      </Head>
      <main>

        <Breadcrumb customItems={[{ index: 2, text: game.name }]} />

        <h2 id="page-title">{game.name}</h2>
        {game.description && <p>{game.description}</p>}

        <Stack direction={{ xs: "column" }} gap={2}>
          <Stack direction={{ xs: "column", sm: "row" }} gap={{ xs: 2 }}>
            <Card style={{ flexGrow: 1, paddingBottom: "6px" }}>
              <h3 style={{ marginLeft: "16px", marginBottom: 0 }}>Details</h3>
              <div style={{ padding: "10px 0" }}>
                <KeyValueList pairs={details} divider={true}/>
              </div>
            </Card>
            <Card style={{ flexGrow: 1, paddingBottom: "6px" }}>
              <div style={{ marginLeft: "16px", marginBottom: "6px" }}>
                <h3>Participants</h3>
                <p style={{ margin: 0 }}>{game.participants.length} of 6 spaces reserved</p>
              </div>
              <List>
                {game.participants.map((username, index) => {
                  return (
                    <ListItem key={index}>
                      <ListItemAvatar><Avatar>{capitalize(username.substring(0, 1))}</Avatar></ListItemAvatar>
                      <ListItemText><span>{username} {username == game.owner && <span>(host)</span>}</span></ListItemText>
                    </ListItem>
                  )
                })}
              </List>
            </Card>
          </Stack>
            <Card style={{padding: "16px"}}>
              <h3 style={{ marginTop: 0 }}>Actions</h3>
              <Stack spacing={2} direction={{ xs: "column", sm: "row" }}>
                {game.owner === username &&
                  <Button variant="outlined" color="error" onClick={handleDelete}>
                    <FontAwesomeIcon icon={faTrash} style={{ marginRight: "8px"}} width={14} height={14} />
                    Permanently delete
                  </Button>
                }
                {!game.participants.includes(username) && game.participants.length < 6 &&
                  <Button variant="outlined" onClick={handleJoin}>
                    <FontAwesomeIcon icon={faCirclePlus} style={{ marginRight: "8px"}} width={14} height={14} />
                    Join
                  </Button>
                }
              </Stack>
            </Card>
        </Stack>
      </main>
    </>
  )
}

const getGame = (response: ResponseType) => {
  if (response && response.data && response.data.detail !== "Not found.") {
    return new Game(response.data);
  }
}

export default GamePage;

export async function getServerSideProps(context: GetServerSidePropsContext) {

  const { clientAccessToken, clientRefreshToken, clientUsername, clientTimezone } = getInitialCookieData(context);
  
  const id = context.params?.id;
  const response = await request('GET', 'games/' + id, clientAccessToken, clientRefreshToken);

  const game = JSON.stringify(getGame(response));

  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUsername: clientUsername,
      clientTimezone: clientTimezone,
      gameId: id,
      initialGame: game ?? null
    }
  };
}