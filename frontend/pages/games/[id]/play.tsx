import { useCallback, useEffect, useState } from 'react';
import Head from 'next/head';
import { GetServerSidePropsContext } from 'next';
import useWebSocket from 'react-use-websocket';

import Card from '@mui/material/Card';

import Game from '@/classes/Game';
import GameParticipant from '@/classes/GameParticipant';
import Faction from '@/classes/Faction';
import FamilySenator from '@/classes/FamilySenator';
import User from '@/classes/User';
import Breadcrumb from '@/components/Breadcrumb';
import PageError from '@/components/PageError';
import getInitialCookieData from '@/functions/cookies';
import request from '@/functions/request';
import { useAuthContext } from '@/contexts/AuthContext';
import { deserializeToInstance, deserializeToInstances } from '@/functions/serialize';

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface PlayGamePageProps {
  initialGame: string;
  initialUsers: string;
  initialGameParticipants: string;
  initialFactions: string;
  initialFamilySenators: string;
  gameId: string;
  clientTimezone: string;
}

const PlayGamePage = (props: PlayGamePageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext();
  const [game, setGame] = useState<Game | undefined>(() => {
    if (props.initialGame) {
      return deserializeToInstance<Game>(Game, props.initialGame);
    }
  });
  const [users, setUsers] = useState<User[]>(() => {
    if (props.initialUsers) {
      return deserializeToInstances<User>(User, props.initialUsers)
    }
    return []
  });
  const [gameParticipants, setGameParticipants] = useState<GameParticipant[]>(() => {
    if (props.initialGameParticipants) {
      return deserializeToInstances<GameParticipant>(GameParticipant, props.initialGameParticipants)
    }
    return []
  });
  const [factions, setFactions] = useState<Faction[]>(() => {
    if (props.initialFactions) {
      return deserializeToInstances<Faction>(Faction, props.initialFactions)
    }
    return []
  });
  const [familySenators, setFamilySenators] = useState<FamilySenator[]>(() => {
    if (props.initialFamilySenators) {
      return deserializeToInstances<FamilySenator>(FamilySenator, props.initialFamilySenators)
    }
    return []
  });

  const gameWebSocketURL = webSocketURL + 'games/' + props.gameId + '/';
  const { lastMessage } = useWebSocket(gameWebSocketURL, {
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
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  const fetchGameParticipants = useCallback(async () => {
    const response = await request('GET', 'game-participants/?game=' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      setGameParticipants(deserializeToInstances<GameParticipant>(GameParticipant, response.data));
    } else {
      setGameParticipants([]);
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  const fetchUsers = useCallback(async () => {
    let users: User[] = []
    gameParticipants.forEach(async (participant) => {
      const response = await request('GET', 'users/' + participant.user, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
      if (response.status === 200) {
        const parsedUser = deserializeToInstance<User>(User, response.data)
        if (parsedUser) users.push(parsedUser)
      }
    })
    setUsers(users);
  }, [gameParticipants, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  const fetchFactions = useCallback(async () => {
    const response = await request('GET', 'factions/?game=' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      setFactions(deserializeToInstances<Faction>(Faction, response.data));
    } else {
      setFactions([]);
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  const fetchFamilySenators = useCallback(async () => {
    const response = await request('GET', 'family-senators/?game=' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      setFamilySenators(deserializeToInstances<FamilySenator>(FamilySenator, response.data));
    } else {
      setFamilySenators([]);
    }
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  useEffect(() => {
    if (lastMessage?.data == "status change") {
      fetchGame();
      fetchGameParticipants();
      fetchFactions();
      fetchFamilySenators();
      fetchUsers();
    }
  }, [lastMessage, fetchGame, fetchGameParticipants, fetchFactions, fetchFamilySenators, fetchUsers])
  
  // Render page error if user is not signed in
  if (user === undefined) {
    return <PageError statusCode={401} />;
  } else if (game == undefined) {
    return <PageError statusCode={404} />
  }

  return (
    <>
      <Head>
        <title>{game ? `Playing ${game.name} | Republic of Rome Online` : 'Loading... | Republic of Rome Online'}</title>
      </Head>
      <main>
        <Breadcrumb customItems={[{ index: 2, text: game.name + " (Lobby)"}]} />

        <h2 id="page-title">{game.name}</h2>
        <section>
          <Card>
            <Card variant='outlined' style={{margin: 0, padding: "16px"}}>
              <h3 style={{ marginTop: 0 }}>Senators</h3>
              {factions.map((faction: Faction) => {
                const gameParticipant = gameParticipants.find(participant => participant.id == faction.player)
                const user = users.find(user => user.id.toString() == gameParticipant?.user)
                return (
                  <div key={faction.id}>
                  <h4>Faction of {user?.username}</h4>
                  <ul>
                    {familySenators.filter((senator: FamilySenator) => {
                      return senator.faction === faction.id
                    }).map((senator: FamilySenator) => {
                      return <li key={senator.id}>{senator.name}</li>
                    })}
                    </ul>
                  </div>
                )
              })}
            </Card>
          </Card>          
        </section>
      </main>
    </>
  )
}

export default PlayGamePage;

export async function getServerSideProps(context: GetServerSidePropsContext) {

  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context);

  const gameId = context.params?.id;

  const gameRequest = request('GET', `games/${gameId}/`, clientAccessToken, clientRefreshToken);
  const gameParticipantRequest = request('GET', `game-participants/?game=${gameId}`, clientAccessToken, clientRefreshToken);
  const factionRequest = request('GET', `factions/?game=${gameId}`, clientAccessToken, clientRefreshToken);
  const senatorRequest = request('GET', `family-senators/?game=${gameId}`, clientAccessToken, clientRefreshToken);

  const [gameResponse, gameParticipantResponse, factionResponse, senatorResponse] = await Promise.all([gameRequest, gameParticipantRequest, factionRequest, senatorRequest]);

  const gameParticipants = deserializeToInstances<GameParticipant>(GameParticipant, gameParticipantResponse.data)

  const users: User[] = (
    await Promise.all(gameParticipants.map(
      async (participant) => {
        const userResponse = await request('GET', `users/${participant.user}/`, clientAccessToken, clientRefreshToken);
        return deserializeToInstance<User>(User, (userResponse.data))
      }
    ))
  ).filter((user): user is User => user !== undefined);

  const gameParticipantsJSON = JSON.stringify(gameParticipants);
  const gameJSON = JSON.stringify(deserializeToInstance<Game>(Game, gameResponse.data));
  const factionsJSON = JSON.stringify(deserializeToInstances<Faction>(Faction, factionResponse.data));
  const familySenatorsJSON = JSON.stringify(deserializeToInstances<FamilySenator>(FamilySenator, senatorResponse.data));
  const usersJSON = JSON.stringify(users);

  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
      clientTimezone: clientTimezone,
      gameId: gameId,
      initialGame: gameJSON ?? null,
      initialGameParticipants: gameParticipantsJSON ?? [],
      initialFactions: factionsJSON ?? [],
      initialFamilySenators: familySenatorsJSON ?? [],
      initialUsers: usersJSON ?? []
    }
  };
}
