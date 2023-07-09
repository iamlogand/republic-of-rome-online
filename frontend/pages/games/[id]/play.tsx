import { useEffect, useState } from 'react';
import Head from 'next/head';
import { GetServerSidePropsContext } from 'next';
import useWebSocket from 'react-use-websocket';

import Card from '@mui/material/Card';

import Game from '@/classes/Game';
import GameParticipant from '@/classes/GameParticipant';
import Faction from '@/classes/Faction';
import FamilySenator from '@/classes/FamilySenator';
import Breadcrumb from '@/components/Breadcrumb';
import PageError from '@/components/PageError';
import getInitialCookieData from '@/functions/cookies';
import request from '@/functions/request';
import { useAuthContext } from '@/contexts/AuthContext';

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? "";

interface PlayGamePageProps {
  initialGame: string;
  initialGameParticipants: string;
  initialFactions: string;
  initialFamilySenators: string;
  gameId: string;
  clientTimezone: string;
}

const PlayGamePage = (props: PlayGamePageProps) => {
  const { username, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const [game, setGame] = useState<Game | undefined>(() => {
    if (props.initialGame) {
      const gameObject = JSON.parse(props.initialGame);
      if (gameObject.name) {  // Might be invalid data, so check for name property
        return new Game(gameObject);
      }
    }
  });
  const [gameParticipants, setGameParticipants] = useState<GameParticipant[]>(() => {
    if (props.initialGameParticipants) {
      const participantObjects = JSON.parse(props.initialGameParticipants);
      return parseGameParticipants(participantObjects)
    }
    return []
  });
  const [factions, setFactions] = useState<Faction[]>(() => {
    if (props.initialFactions) {
      const factionObjects = JSON.parse(props.initialFactions);
      return parseFactions(factionObjects)
    }
    return []
  });
  const [familySenators, setFamilySenators] = useState<FamilySenator[]>(() => {
    if (props.initialFamilySenators) {
      const senatorObjects = JSON.parse(props.initialFamilySenators);
      return parseFamilySenators(senatorObjects)
    }
    return []
  });

  const gameWebSocketURL = webSocketURL + 'games/' + props.gameId + '/';
  const { lastMessage } = useWebSocket(gameWebSocketURL, {
    onOpen: () => console.log('WebSocket connection opened'),
    // Attempt to reconnect on all close events, such as server shutting down
    shouldReconnect: (closeEvent) => true,
  });

  const fetchGame = async () => {
    const response = await request('GET', 'games/' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
    if (response.status === 200) {
      setGame(parseGame(response.data));
    } else {
      setGame(undefined);
    }
  }

  const fetchGameParticipants = async () => {
    const response = await request('GET', 'game-participants/?game=' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
    if (response.status === 200) {
      setGameParticipants(parseGameParticipants(response.data));
    } else {
      setGameParticipants([]);
    }
  }

  const fetchFactions = async () => {
    const response = await request('GET', 'factions/?game=' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
    if (response.status === 200) {
      setFactions(parseFactions(response.data));
    } else {
      setFactions([]);
    }
  }

  const fetchFamilySenators = async () => {
    const response = await request('GET', 'family-senators/?game=' + props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
    if (response.status === 200) {
      setFamilySenators(parseFamilySenators(response.data));
    } else {
      setFamilySenators([]);
    }
  }

  useEffect(() => {
    if (lastMessage?.data == "status change") {
      fetchGame();
      fetchGameParticipants();
      fetchFactions();
      fetchFamilySenators();
    }
  }, [lastMessage])

  useEffect(() => {
    fetchGame();
    fetchGameParticipants();
    fetchFactions();
    fetchFamilySenators();
  }, [props.gameId, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername])
  
  // Render page error if user is not signed in
  if (username === '') {
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
                return (
                  <div key={faction.id}>
                  <h4>Faction {faction.position}</h4>
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

const parseGame = (data: any) => {
  if (data && data.detail !== "Not found.") {
    return new Game(data);
  }
}

const parseGameParticipants = (data: any) => {
  if (data && data.length > 0) {
    let participants: GameParticipant[] = []
    data.forEach((participantData: any) => {
      const participant = parseGameParticipant(participantData)
      participants.push(participant)
    })
    return participants;
  } else {
    return []
  }
}

const parseGameParticipant = (data: any) => {
  return new GameParticipant(data.id, data.game, data.position, data.player)
}

const parseFactions = (data: any) => {
  if (data && data.length > 0) {
    let factions: Faction[] = []
    data.forEach((factionData: any) => {
      const faction = parseFaction(factionData)
      factions.push(faction)
    })
    return factions;
  } else {
    return []
  }
}

const parseFaction = (data: any) => {
  return new Faction(data.id, data.game, data.position, data.player)
}

const parseFamilySenators = (data: any) => {
  if (data && data.length > 0) {
    let games: FamilySenator[] = []
    data.forEach((senatorData: any) => {
      const senator = parseFamilySenator(senatorData)
      games.push(senator)
    })
    return games;
  } else {
    return []
  }
}

const parseFamilySenator = (data: any) => {
  return new FamilySenator(data.id, data.name, data.game, data.faction)
}

export default PlayGamePage;

export async function getServerSideProps(context: GetServerSidePropsContext) {

  const { clientAccessToken, clientRefreshToken, clientUsername, clientTimezone } = getInitialCookieData(context);

  const gameId = context.params?.id;

  const gameRequest = request('GET', `games/${gameId}/`, clientAccessToken, clientRefreshToken);
  const gameParticipantRequest = request('GET', `game-participants/?game=${gameId}`, clientAccessToken, clientRefreshToken);
  const factionRequest = request('GET', `factions/?game=${gameId}`, clientAccessToken, clientRefreshToken);
  const senatorRequest = request('GET', `family-senators/?game=${gameId}`, clientAccessToken, clientRefreshToken);

  const [gameResponse, gameParticipantResponse, factionResponse, senatorResponse] = await Promise.all([gameRequest, gameParticipantRequest, factionRequest, senatorRequest]);

  const game = JSON.stringify(parseGame(gameResponse.data));
  const gameParticipants = JSON.stringify(parseGameParticipants(gameParticipantResponse.data));
  const factions = JSON.stringify(parseFactions(factionResponse.data));
  const familySenators = JSON.stringify(parseFamilySenators(senatorResponse.data));

  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUsername: clientUsername,
      clientTimezone: clientTimezone,
      gameId: gameId,
      initialGame: game ?? null,
      initialGameParticipants: gameParticipants ?? [],
      initialFactions: factions ?? [],
      initialFamilySenators: familySenators ?? []
    }
  };
}
