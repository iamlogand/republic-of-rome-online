import { GetServerSidePropsContext } from 'next';
import Head from 'next/head';
import { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';
import { faCheck } from '@fortawesome/free-solid-svg-icons';
import Game from '@/classes/Game';
import Breadcrumb from '@/components/Breadcrumb';
import Button from '@/components/Button';
import PageError from '@/components/PageError';
import { useAuthContext } from '@/contexts/AuthContext';
import getInitialCookieData from '@/functions/cookies';
import formatDate from '@/functions/date';
import request, { ResponseType } from '@/functions/request';
import router from 'next/router';

interface GamePageProps {
  initialGame: string;
  gameId: string;
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
  const [deleted, setDeleted] = useState<boolean>(false);

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
        setDeleted(true);
        setTimeout(async () => await router.push('/games/'), 1000);
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

  return (
    <>
      <Head>
        <title>Game Lobby - Republic of Rome Online</title>
      </Head>
      <main>

        <Breadcrumb customItems={[{index: 2, text: game.name},]} />

        <h2 id="page-title">Game Lobby</h2>
        
        <div className='table-container' style={{maxWidth: "100%"}}>
          <table>
            <thead>
              <tr>
                <th scope="row" style={{width: "140px"}}>Name</th>
                <td>{game.name}</td>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Owner</th>
                <td>{game.owner === username ? <b>You</b> : game.owner}</td>
              </tr>
              <tr>
                <th scope="row">Description</th>
                <td>{game.description}</td>
              </tr>
              <tr>
                <th scope="row">Creation Date</th>
                <td>{game.creation_date && game.creation_date instanceof Date && formatDate(game.creation_date)}</td>
              </tr>
              <tr>
                <th scope="row">Start Date</th>
                <td>{game.start_date && game.start_date instanceof Date && formatDate(game.start_date)}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {game.owner === username &&
          <>
            <h3>Actions</h3>
            <Button onClick={deleted ? null : handleDelete} styleType='danger' width={200}>
              {deleted ?
                <>
                  <FontAwesomeIcon icon={faCheck} style={{ marginRight: "8px"}} width={14} height={14} />
                  <b>Deleted</b>
                </>
                :
                <>
                  <FontAwesomeIcon icon={faTrash} style={{ marginRight: "8px"}} width={14} height={14} />
                  Permanently delete
                </>
              }
            </Button>
          </>
        }
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

  const { ssrAccessToken, ssrRefreshToken, ssrUsername } = getInitialCookieData(context);
  
  const id = context.params?.id;
  const response = await request('GET', 'games/' + id, ssrAccessToken, ssrRefreshToken);

  const game = JSON.stringify(getGame(response));

  return {
    props: {
      ssrEnabled: true,
      ssrAccessToken: ssrAccessToken,
      ssrRefreshToken: ssrRefreshToken,
      ssrUsername: ssrUsername,
      gameId: id,
      initialGame: game ?? null
    }
  };
}