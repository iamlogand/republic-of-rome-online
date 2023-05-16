import { useEffect, useState } from 'react';
import { GetServerSidePropsContext } from 'next';
import router from 'next/router';
import Head from 'next/head';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Card from '@mui/material/Card';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';

import Game from '@/classes/Game';
import Breadcrumb from '@/components/Breadcrumb';
import PageError from '@/components/PageError';
import { useAuthContext } from '@/contexts/AuthContext';
import getInitialCookieData from '@/functions/cookies';
import formatDate from '@/functions/date';
import request, { ResponseType } from '@/functions/request';
import KeyValueStack from '@/components/KeyValueStack';

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
      console.log("deleting...")
      const response = await request('DELETE', 'games/' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
      if (response.status === 204) {
        router.push('/games/');
      }
    }
    deleteGame();
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

  const getFormattedParticipants = () => {
    if (game.participants && game.participants.length > 0) {
      return game.participants.join(", ") ?? "";
    } else {
      return "";
    }
  }

  const fields = [
    { name: "Name", value: game.name},
    { name: "Owner", value: game.owner ?? ''},
    { name: "Description", value: game.description ?? ''},
    { name: "Creation Date", value: formatDate(game.creation_date, props.clientTimezone) },
    { name: "Start Date", value: getFormattedStartDate() },
    { name: "Participants", value: getFormattedParticipants() }
  ]

  return (
    <>
      <Head>
        <title>Game Lobby - Republic of Rome Online</title>
      </Head>
      <main>

        <Breadcrumb customItems={[{ index: 2, text: game.name }]} />

        <h2 id="page-title">Game Lobby</h2>

        <Stack direction={{ xs: "column" }} gap={3}>
          <Card variant="outlined">
            <KeyValueStack fields={fields} />
          </Card>

          {game.owner === username &&
            <Card variant="outlined" style={{ padding: "16px" }}>
              <h3 style={{ marginTop: 0 }}>Actions</h3>
              <Button variant="outlined" color="error" onClick={handleDelete}>
                <FontAwesomeIcon icon={faTrash} style={{ marginRight: "8px"}} width={14} height={14} />
                Permanently delete
              </Button>
            </Card>
          }
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