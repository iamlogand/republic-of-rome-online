import Game from '@/classes/Game';
import Button from '@/components/Button';
import { useAuthContext } from '@/contexts/AuthContext';
import getInitialCookieData from '@/functions/cookies';
import formatDate from '@/functions/date';
import request from '@/functions/request';
import { AxiosResponse } from 'axios';
import { GetServerSidePropsContext } from 'next';
import Head from 'next/head';
import { useState } from 'react';

const GamePage = ({ initialGame }: { initialGame: string }) => {
  const { username } = useAuthContext();
  const [game] = useState<Game>(() => {
    const gameObj = JSON.parse(initialGame);
    return new Game(
      gameObj.id,
      gameObj.name,
      gameObj.owner,
      gameObj.description,
      new Date(gameObj.creationDate),
      gameObj.startDate ? new Date(gameObj.startDate) : null
    );
  });

  return (
    <>
      <Head>
        <title>Game Dashboard - Republic of Rome Online</title>
      </Head>
      <main>
        <section className='row'>
          <Button href="/games">◀&nbsp; Back</Button>
          <h2 id="page-title">Game Dashboard</h2>
        </section>
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
                <td>{game.owner == username ? <b>You</b> : game.owner}</td>
              </tr>
              <tr>
                <th scope="row">Description</th>
                <td>{game.description}</td>
              </tr>
              <tr>
                <th scope="row">Creation Date</th>
                <td>{game.creationDate && game.creationDate instanceof Date && formatDate(game.creationDate)}</td>
              </tr>
              <tr>
                <th scope="row">Start Date</th>
                <td>{game.startDate && game.startDate instanceof Date && formatDate(game.startDate)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </>
  )
}

const getGame = (response: AxiosResponse) => {
  if (response && response.data) {
    const object = response.data;
    return new Game(
      object["id"],
      object["name"],
      object["owner"],
      object["description"] ?? null,
      new Date(object["creation_date"]),
      object["start_date"] ? new Date(object["start_date"]) : null
    );
  }
}

export default GamePage;

// This page depends completely on SSR to get the game data
export async function getServerSideProps(context: GetServerSidePropsContext) {

  const { accessToken, refreshToken, username } = getInitialCookieData(context);
  
  const id = context?.params?.id;
  let game = null;
  if (id != null) {
    const response = await request('GET', 'games/' + id, accessToken, refreshToken);
    game = JSON.stringify(getGame(response));
  }

  return {
    props: {
      ssrAccessToken: accessToken,
      ssrRefreshToken: refreshToken,
      ssrUsername: username,
      initialGame: game
    }
  };
}