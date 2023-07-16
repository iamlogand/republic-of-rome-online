import { useEffect, useState } from 'react';
import { GetServerSidePropsContext } from 'next';
import router from 'next/router';
import Head from 'next/head';
import useWebSocket from 'react-use-websocket';

import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { capitalize } from '@mui/material/utils';
import TextField from '@mui/material/TextField';

import Game from '@/classes/Game';
import Breadcrumb from '@/components/Breadcrumb';
import PageError from '@/components/PageError';
import { useAuthContext } from '@/contexts/AuthContext';
import getInitialCookieData from '@/functions/cookies';
import request, { ResponseType } from '@/functions/request';

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface GamePageProps {
  initialGame: string;
  gameId: string;
  clientTimezone: string;
}

const EditGamePage = (props: GamePageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext();
  const [game, setGame] = useState<Game | null>(() => {
    if (props.initialGame) {
      const gameObject = JSON.parse(props.initialGame);
      if (gameObject.name) {  // Might be invalid data, so check for name property
        return new Game(gameObject);
      }
    }
    return null
  });
  const [description, setDescription] = useState<string>(game?.description ?? "");
  const [descriptionFeedback, setDescriptionFeedback] = useState<string>('');

  const gameWebSocketURL = webSocketURL + 'games/' + props.gameId + '/';
  const { sendMessage } = useWebSocket(gameWebSocketURL, {
    onOpen: () => console.log('WebSocket connection opened'),
    // Attempt to reconnect on all close events, such as server shutting down
    shouldReconnect: (closeEvent) => true,
  });

  const handleDescriptionChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDescription(event.target.value);
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const gameData = {
      description: description
    }

    const response = await request('PATCH', 'games/' + props.gameId + '/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser, gameData);
    if (response) {
      console.log(response.status)
      if (response.status === 200) {
        sendMessage('status change');
        await router.push('/games/' + game?.id);
      } else {
        if (response.data) {
          if (response.data.description && Array.isArray(response.data.description) && response.data.description.length > 0) {
            setDescriptionFeedback(response.data.description[0]);
          } else {
            setDescriptionFeedback('');
          }
        }
      }
    }
  }

  // Render page error if user is not signed in or not game owner
  if (user === null || (game !== null && (game?.host !== user?.username || game.step !== 0))) {
    return <PageError statusCode={401} />;
  } else if (game == null) {
    return <PageError statusCode={404} />
  }

  return (
    <>
      <Head>
        <title>{game ? `Editing ${game.name} | Republic of Rome Online` : 'Loading... | Republic of Rome Online'}</title>
      </Head>
      <main>

        <Breadcrumb customItems={[{ index: 2, text: game.name }]} />

        <h2 id="page-title">Edit Game - {game.name}</h2>
        <section>
          <form onSubmit={handleSubmit}>
            <Stack alignItems={"start"} spacing={2}>
              <TextField multiline
                id="description"
                label="Description"
                value={description}
                error={descriptionFeedback != ""}
                onChange={handleDescriptionChange}
                rows={3}
                style={{ width: "100%" }}
                helperText={capitalize(descriptionFeedback)} />

              <Button variant="contained" type="submit">Save</Button>
            </Stack>
          </form>
        </section>
      </main>
    </>
  )
}

const getGame = (response: ResponseType) => {
  if (response && response.data && response.data.detail !== "Not found.") {
    return new Game(response.data);
  }
}

export default EditGamePage;

export async function getServerSideProps(context: GetServerSidePropsContext) {

  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context);
  
  const id = context.params?.id;
  const response = await request('GET', 'games/' + id, clientAccessToken, clientRefreshToken);

  const game = JSON.stringify(getGame(response));

  return {
    props: {
      ssrEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
      clientTimezone: clientTimezone,
      gameId: id,
      initialGame: game ?? null
    }
  };
}
