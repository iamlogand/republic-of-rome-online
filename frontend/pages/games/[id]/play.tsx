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
import request, { ResponseType } from '@/functions/request';
import { useAuthContext } from '@/contexts/AuthContext';
import { deserializeToInstance, deserializeToInstances } from '@/functions/serialize';

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface PlayGamePageProps {
  clientTimezone: string
  gameId: string
  authFailure: boolean
  initialGame: string
  initialUsers: string
  initialGameParticipants: string
  initialFactions: string
  initialFamilySenators: string
}

const PlayGamePage = (props: PlayGamePageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext();
  const [game, setGame] = useState<Game | null>(() => {
    if (props.initialGame) {
      return deserializeToInstance<Game>(Game, props.initialGame);
    }
    return null
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
      setGame(null);
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
  if (user === null || props.authFailure) {
    return <PageError statusCode={401} />;
  } else if (game === null || factions.length === 0) {
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

// The game, participants, factions, senators and users are retrieved by the frontend server
export async function getServerSideProps(context: GetServerSidePropsContext) {

  // Get client cookie data from the page request
  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context);

  // Get game ID from the URL
  const gameId = context.params?.id;

  // Asynchronously retrieve the game, participants, factions and senators
  const gameRequest = request('GET', `games/${gameId}/`, clientAccessToken, clientRefreshToken);
  const gameParticipantsRequest = request('GET', `game-participants/?game=${gameId}`, clientAccessToken, clientRefreshToken);
  const factionsRequest = request('GET', `factions/?game=${gameId}`, clientAccessToken, clientRefreshToken);
  const familySenatorsRequest = request('GET', `family-senators/?game=${gameId}`, clientAccessToken, clientRefreshToken);
  const [gameResponse, gameParticipantsResponse, factionsResponse, familySenatorsResponse] = await Promise.all(
    [gameRequest, gameParticipantsRequest, factionsRequest, familySenatorsRequest]
  );

  // Track whether there has been an authentication failure due to bad credentials
  let authFailure = false

  // Use the game participants to figure out which users to retrieve
  // and asynchronously retrieve these users
  let userResponses: ResponseType[] = []
  if (gameParticipantsResponse.status == 200) {
    const gameParticipants = deserializeToInstances<GameParticipant>(GameParticipant, gameParticipantsResponse.data)
    userResponses = await Promise.all(gameParticipants.map(
      async (participant: GameParticipant) => {
        return request('GET', `users/${participant.user}/`, clientAccessToken, clientRefreshToken);
      }
    ))
  } else if (gameParticipantsResponse.status == 401) {
    userResponses = []
    authFailure = true
  }

  // Deserialize the users, put them in a list, then serialize the whole list
  // This is done so that initial users is a JSON string not a list of JSON strings
  let users: User[] = []
  userResponses.map((response: ResponseType) => {

    // Ensure response is OK before deserialization
    if (response.status == 200) {
      const user = deserializeToInstance<User>(User, response.data)
      if (user) users.push(user)
    } else if (gameResponse.status === 401) {
      authFailure = true
    }
  })
  const usersJSON = JSON.stringify(users)

  // Ensure that the remaining responses are OK before getting data
  let gameJSON = null
  let gameParticipantsJSON = null
  let factionsJSON = null
  let familySenatorsJSON = null
  if (gameResponse.status === 200 && gameParticipantsResponse.status === 200 &&
    factionsResponse.status === 200 && familySenatorsResponse.status === 200) {
    gameJSON = gameResponse.data
    gameParticipantsJSON = gameParticipantsResponse.data
    factionsJSON = factionsResponse.data
    familySenatorsJSON = familySenatorsResponse.data
  } else if (gameResponse.status === 401 || gameParticipantsResponse.status === 401 ||
    factionsResponse.status === 401 || factionsResponse.status === 401) {
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
      initialGame: gameJSON,
      initialGameParticipants: gameParticipantsJSON,
      initialFactions: factionsJSON,
      initialFamilySenators: familySenatorsJSON,
      initialUsers: usersJSON
    }
  };
}
