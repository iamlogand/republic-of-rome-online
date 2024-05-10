import {
  Dispatch,
  SetStateAction,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react"
import Head from "next/head"
import useWebSocket from "react-use-websocket"

import Tabs from "@mui/material/Tabs"
import Tab from "@mui/material/Tab"
import CircularProgress from "@mui/material/CircularProgress"

import { useGameContext } from "@/contexts/GameContext"
import Game from "@/classes/Game"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import Title from "@/classes/Title"
import PageError from "@/components/PageError"
import request from "@/functions/request"
import { useCookieContext } from "@/contexts/CookieContext"
import {
  deserializeToInstance,
  deserializeToInstances,
} from "@/functions/serialize"
import Collection from "@/classes/Collection"
import SenatorList from "@/components/SenatorList"
import FactionList from "@/components/FactionList"
import DetailSection from "@/components/DetailSection"
import Turn from "@/classes/Turn"
import Phase from "@/classes/Phase"
import Step from "@/classes/Step"
import MetaSection from "@/components/MetaSection"
import Action from "@/classes/Action"
import ProgressSection from "@/components/ProgressSection"
import ActionLog from "@/classes/ActionLog"
import refreshAccessToken from "@/functions/tokens"
import SenatorActionLog from "@/classes/SenatorActionLog"
import Secret from "@/classes/Secret"
import War from "@/classes/War"
import WarfareTab from "@/components/WarfareTab"
import EnemyLeader from "@/classes/EnemyLeader"
import SenateTab from "@/components/SenateTab"
import Concession from "@/classes/Concession"

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? ""

// Props are passed here from the `GamePageWrapper`
export interface GamePageProps {
  clientTimezone: string
  gameId: string
  authFailure: boolean
  initialGame: string
  initialLatestSteps: string
}

// The game page component - the most important component in the frontend project.
// This would be an actual page if it wasn't wrapped by `GamePageWrapper`, which supplies `GameContext`
const GamePage = (props: GamePageProps) => {
  const {
    accessToken,
    refreshToken,
    user,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useCookieContext()
  const [syncingGameData, setSyncingGameData] = useState<boolean>(true)
  const [latestTokenRefreshDate, setLatestTokenRefreshDate] =
    useState<Date | null>(null)
  const [refreshingToken, setRefreshingToken] = useState<boolean>(false)

  // Game-specific state
  const {
    game,
    setGame,
    setTurns,
    setPhases,
    steps,
    setSteps,
    allPlayers,
    setAllPlayers,
    setAllFactions,
    setAllSenators,
    setAllTitles,
    setAllConcessions,
    setSenatorActionLogs,
    setNotifications,
    setAllSecrets,
    setWars,
    setEnemyLeaders,
    latestActions,
    setLatestActions,
  } = useGameContext()

  // Set game-specific state using initial data
  useEffect(() => {
    setGame(
      props.initialGame
        ? deserializeToInstance<Game>(Game, props.initialGame)
        : null
    )
  }, [props.initialGame, setGame])

  // UI selections
  const [mainTab, setMainTab] = useState(0)
  const [mainSenatorListSort, setMainSenatorListSort] = useState<string>("")
  const [mainSenatorListFilterAlive, setMainSenatorListFilterAlive] =
    useState<boolean>(true)
  const [mainSenatorListFilterDead, setMainSenatorListFilterDead] =
    useState<boolean>(false)

  // Establish a WebSocket connection to the game group and provide a state containing the last message
  const { lastMessage: lastGameMessage } = useWebSocket(
    webSocketURL + `games/${props.gameId}/?token=${accessToken}`,
    {
      // On connection open perform a full sync
      onOpen: () => {
        console.log("Game WebSocket connection opened")
        fullSync()
        setLatestTokenRefreshDate(new Date())
      },

      // On connection close refresh the access token in case their access token has expired
      onClose: async () => {
        console.log("Game WebSocket connection closed (or failed to connect)")

        if (refreshingToken) return // Don't refresh access token if already being refreshed

        if (user === null) setSyncingGameData(false)

        // Refresh the access token if it hasn't been refreshed yet or is 1 hour old
        if (
          latestTokenRefreshDate === null ||
          (latestTokenRefreshDate &&
            latestTokenRefreshDate.getTime() < Date.now() - 1000 * 60 * 59)
        ) {
          console.log("Refreshing access token")
          setRefreshingToken(true)
          await refreshAccessToken(
            refreshToken,
            setAccessToken,
            setRefreshToken,
            setUser
          )
          setLatestTokenRefreshDate(new Date())
          setRefreshingToken(false)
        }
      },

      shouldReconnect: () => (user ? true : false),
    }
  )

  // Establish a WebSocket connection to the player group and provide a state containing the last message
  let thisPlayerId: number | null = null
  if (user) {
    thisPlayerId =
      allPlayers.asArray.find((p) => p.user?.id === user.id)?.id ?? null
  }
  const { lastMessage: lastPlayerMessage } = useWebSocket(
    webSocketURL + `players/${thisPlayerId}/?token=${accessToken}`,
    {
      // On connection open perform a full sync
      onOpen: () => {
        console.log("Player WebSocket connection opened")
      },

      // On connection close refresh the access token in case their access token has expired
      onClose: async () => {
        console.log("Player WebSocket connection closed (or failed to connect)")
      },

      shouldReconnect: () => (user ? true : false),
    }
  )

  const fetchData = useCallback(
    async (
      url: string,
      onSuccess: (data: any) => void,
      onError: () => void
    ) => {
      const response = await request(
        "GET",
        url,
        accessToken,
        refreshToken,
        setAccessToken,
        setRefreshToken,
        setUser
      )
      if (response.status === 200) {
        onSuccess(response.data)
      } else {
        onError()
      }
    },
    [accessToken, refreshToken, setAccessToken, setRefreshToken, setUser]
  )

  const fetchAndSetInstance = useCallback(
    <Entity extends { id: number }>(
      EntityType: EntityConstructor<Entity>,
      setEntity: Dispatch<SetStateAction<Entity | null>>,
      url: string
    ) => {
      fetchData(
        url,
        (data: any) => {
          if (data.length === 0) return // Exit if there is no data
          const deserializedInstance = new EntityType(data.id ? data : data[0])
          setEntity(deserializedInstance)
        },
        () => {}
      )
    },
    [fetchData]
  )

  type EntityConstructor<Entity> = new (data: any) => Entity

  const fetchAndSetCollection = useCallback(
    <Entity extends { id: number }>(
      EntityType: EntityConstructor<Entity>,
      setEntity: Dispatch<SetStateAction<Collection<Entity>>>,
      url: string
    ) => {
      fetchData(
        url,
        (data: any) => {
          const deserializedInstances = data.map(
            (item: any) => new EntityType(item)
          )
          setEntity(new Collection<Entity>(deserializedInstances))
        },
        () => {
          setEntity(new Collection<Entity>())
        }
      )
    },
    [fetchData]
  )

  const fetchGame = useCallback(() => {
    const url = `games/${props.gameId}/?prefetch_user`
    fetchAndSetInstance(Game, setGame, url)
  }, [props.gameId, setGame, fetchAndSetInstance])

  const fetchPlayers = useCallback(async () => {
    const url = `players/?game=${props.gameId}&prefetch_user`
    fetchAndSetCollection(Player, setAllPlayers, url)
  }, [props.gameId, setAllPlayers, fetchAndSetCollection])

  const fetchFactions = useCallback(async () => {
    const url = `factions/?game=${props.gameId}`
    fetchAndSetCollection(Faction, setAllFactions, url)
  }, [props.gameId, setAllFactions, fetchAndSetCollection])

  const fetchSenators = useCallback(async () => {
    const url = `senators/?game=${props.gameId}`
    fetchAndSetCollection(Senator, setAllSenators, url)
  }, [props.gameId, setAllSenators, fetchAndSetCollection])

  const fetchWars = useCallback(async () => {
    const url = `wars/?game=${props.gameId}`
    fetchAndSetCollection(War, setWars, url)
  }, [props.gameId, setWars, fetchAndSetCollection])

  const fetchEnemyLeaders = useCallback(async () => {
    const url = `enemy-leaders/?game=${props.gameId}`
    fetchAndSetCollection(EnemyLeader, setEnemyLeaders, url)
  }, [props.gameId, setEnemyLeaders, fetchAndSetCollection])

  const fetchTitles = useCallback(async () => {
    const url = `titles/?game=${props.gameId}&relevant`
    fetchAndSetCollection(Title, setAllTitles, url)
  }, [props.gameId, setAllTitles, fetchAndSetCollection])

  const fetchConcessions = useCallback(async () => {
    const url = `concessions/?game=${props.gameId}`
    fetchAndSetCollection(Concession, setAllConcessions, url)
  }, [props.gameId, setAllConcessions, fetchAndSetCollection])

  const fetchTurns = useCallback(async () => {
    const url = `turns/?game=${props.gameId}`
    fetchAndSetCollection(Turn, setTurns, url)
  }, [props.gameId, setTurns, fetchAndSetCollection])

  const fetchPhases = useCallback(async () => {
    const url = `phases/?game=${props.gameId}`
    fetchAndSetCollection(Phase, setPhases, url)
  }, [props.gameId, setPhases, fetchAndSetCollection])

  const fetchSteps = useCallback(async () => {
    const url = `steps/?game=${props.gameId}`
    fetchAndSetCollection(Step, setSteps, url)
  }, [props.gameId, setSteps, fetchAndSetCollection])

  const fetchLatestActions = useCallback(async () => {
    const url = `actions/?game=${props.gameId}&latest`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<Action>(
          Action,
          data
        )
        setLatestActions(new Collection<Action>(deserializedInstances))
      },
      () => {
        setLatestActions(new Collection<Action>())
      }
    )
  }, [props.gameId, setLatestActions, fetchData])

  const fetchSecrets = useCallback(async () => {
    fetchData(
      `secrets-private/?game=${props.gameId}`,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<Secret>(
          Secret,
          data
        )
        setAllSecrets((instances) => {
          // Merge the new notifications with the existing ones
          // Loop over each new notification and add it to the collection if it doesn't already exist
          for (const newInstance of deserializedInstances) {
            if (!instances.allIds.includes(newInstance.id)) {
              instances = instances.add(newInstance)
            } else if (instances.allIds.includes(newInstance.id)) {
              // If the instance already exists, update it
              instances = instances.update(newInstance)
            }
          }
          return instances
        })
      },
      () => {}
    )
    fetchData(
      `secrets-public/?game=${props.gameId}`,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<Secret>(
          Secret,
          data
        )
        setAllSecrets((instances) => {
          // Merge the new instances with the existing ones
          // Loop over each new instance and add it to the collection if it doesn't already exist
          for (const newInstance of deserializedInstances) {
            if (!instances.allIds.includes(newInstance.id)) {
              instances = instances.add(newInstance)
            }
          }
          return instances
        })
      },
      () => {}
    )
  }, [props.gameId, setAllSecrets, fetchData])

  const fetchNotifications = useCallback(async () => {
    const minIndex = -50 // Fetch the last 50 notifications
    const maxIndex = -1
    const url = `action-logs/?game=${props.gameId}&min_index=${minIndex}&max_index=${maxIndex}`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<ActionLog>(
          ActionLog,
          data
        )
        setNotifications((notifications) => {
          // Merge the new notifications with the existing ones
          // Loop over each new notification and add it to the collection if it doesn't already exist
          for (const newInstance of deserializedInstances) {
            if (!notifications.allIds.includes(newInstance.id)) {
              notifications = notifications.add(newInstance)
            }
          }
          return notifications
        })
      },
      () => {}
    )
  }, [props.gameId, setNotifications, fetchData])

  // Fully synchronize all game data
  const fullSync = useCallback(async () => {
    if (user === null) {
      console.log("[Full Sync] skipped because user is not signed in")
      return // Don't attempt to sync if user is not signed in
    }
    if (refreshingToken) {
      console.log("[Full Sync] skipped because access token is being refreshed")
      return // Don't attempt to sync if access token is being refreshed
    }

    console.log("[Full Sync] started")
    const startTime = performance.now()

    setSyncingGameData(true)

    // Fetch game data
    const requestsBatch1 = [
      fetchSteps(), // Positional
      fetchGame(),
      fetchPlayers(),
      fetchFactions(),
      fetchSenators(),
      fetchTitles(),
      fetchConcessions(),
      fetchTurns(),
      fetchPhases(),
      fetchNotifications(),
      fetchSecrets(),
      fetchWars(),
      fetchEnemyLeaders(),
      fetchLatestActions(),
    ]
    await Promise.all(requestsBatch1)

    setSyncingGameData(false)

    // Track time taken to sync
    const endTime = performance.now()
    const timeTaken = Math.round(endTime - startTime)

    console.log(`[Full Sync] completed in ${timeTaken}ms`)
  }, [
    refreshingToken,
    user,
    fetchGame,
    fetchPlayers,
    fetchFactions,
    fetchSenators,
    fetchTitles,
    fetchConcessions,
    fetchTurns,
    fetchPhases,
    fetchSteps,
    fetchLatestActions,
    fetchNotifications,
    fetchSecrets,
    fetchWars,
    fetchEnemyLeaders,
  ])

  // Function to handle instance updates
  const handleInstanceUpdate = useCallback(
    <Entity extends { id: number }>(
      setFunction: Dispatch<SetStateAction<Entity | null>>,
      EntityType: EntityConstructor<Entity>,
      message: any
    ) => {
      if (message?.operation == "create") {
        const instance = deserializeToInstance<Entity>(
          EntityType,
          message.instance.data
        )
        if (instance) {
          setFunction(instance)
        }
      } else if (message?.operation == "destroy") {
        setFunction(null)
      }
    },
    []
  )

  // Function to handle collection updates
  const handleCollectionUpdate = useCallback(
    <Entity extends { id: number }>(
      setFunction: Dispatch<SetStateAction<Collection<Entity>>>,
      EntityType: EntityConstructor<Entity>,
      message: any
    ) => {
      if (message?.operation == "create") {
        const instance = deserializeToInstance<Entity>(
          EntityType,
          message.instance.data
        )
        if (instance) {
          setFunction((instances) => {
            if (instances.allIds.includes(instance.id)) {
              const existingInstance = instances.byId[instance.id]

              // If the new instance is a public version of an existing private instance, keep the existing private instance
              if (
                "private_version" in instance &&
                !instance.private_version &&
                "private_version" in existingInstance &&
                existingInstance.private_version
              ) {
                return instances
              }
              return instances.update(instance)
            } else {
              return instances.add(instance)
            }
          })
        }
      } else if (message?.operation == "destroy") {
        setFunction((instances) => instances.remove(message.instance.id))
      }
    },
    []
  )

  type ClassUpdateMap = {
    [key: string]: [
      React.Dispatch<React.SetStateAction<any>>,
      new (data: any) => any,
      (
        setFunction: React.Dispatch<React.SetStateAction<any>>,
        ClassType: new (data: any) => any,
        message: any
      ) => void
    ]
  }

  const classUpdateMap: ClassUpdateMap = useMemo(
    () => ({
      turn: [setTurns, Turn, handleCollectionUpdate],
      phase: [setPhases, Phase, handleCollectionUpdate],
      step: [setSteps, Step, handleCollectionUpdate],
      game: [setGame, Game, handleInstanceUpdate],
      faction: [setAllFactions, Faction, handleCollectionUpdate],
      senator: [setAllSenators, Senator, handleCollectionUpdate],
      action: [setLatestActions, Action, handleCollectionUpdate],
      title: [setAllTitles, Title, handleCollectionUpdate],
      concession: [setAllConcessions, Concession, handleCollectionUpdate],
      action_log: [setNotifications, ActionLog, handleCollectionUpdate],
      senator_action_log: [
        setSenatorActionLogs,
        SenatorActionLog,
        handleCollectionUpdate,
      ],
      war: [setWars, War, handleCollectionUpdate],
      enemy_leader: [setEnemyLeaders, EnemyLeader, handleCollectionUpdate],
      secret: [setAllSecrets, Secret, handleCollectionUpdate],
    }),
    [
      handleCollectionUpdate,
      handleInstanceUpdate,
      setGame,
      setTurns,
      setPhases,
      setSteps,
      setLatestActions,
      setAllFactions,
      setAllTitles,
      setAllConcessions,
      setAllSenators,
      setNotifications,
      setSenatorActionLogs,
      setWars,
      setEnemyLeaders,
      setAllSecrets,
    ]
  )

  // Use message payloads to update state
  const processMessages = useCallback(
    (lastMessage: MessageEvent<any> | null) => {
      if (lastMessage?.data) {
        const deserializedData = JSON.parse(lastMessage.data)
        if (deserializedData && deserializedData.length > 0) {
          for (const message of deserializedData) {
            if (
              message?.operation == "create" ||
              message?.operation == "destroy"
            ) {
              const [setFunction, ClassType, handleUpdate] =
                classUpdateMap[
                  message.instance.class as keyof typeof classUpdateMap
                ]
              if (setFunction && ClassType && handleUpdate) {
                handleUpdate(setFunction, ClassType, message)
              }
            }
          }
        }
      }
    },
    [classUpdateMap]
  )

  // Read game WebSocket messages
  useEffect(() => {
    processMessages(lastGameMessage)
  }, [lastGameMessage, processMessages])

  // Read player WebSocket messages
  useEffect(() => {
    processMessages(lastPlayerMessage)
  }, [lastPlayerMessage, processMessages])

  // Remove old actions (i.e. actions from a step that is no longer the latest step)
  useEffect(() => {
    const latestStep = steps.asArray.sort((a, b) => a.id - b.id)[
      steps.asArray.length - 1
    ]
    if (!latestStep) return
    if (latestActions.asArray.some((a) => a.step < latestStep?.id)) {
      setLatestActions(
        (actions) =>
          new Collection<Action>(
            actions.asArray.filter((a) => a.step === latestStep?.id)
          )
      )
    }
  }, [latestActions, setLatestActions, steps])

  const handleMainTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setMainTab(newValue)
  }

  // Sign out if authentication failed on the server
  useEffect(() => {
    if (props.authFailure) {
      setAccessToken("")
      setRefreshToken("")
      setUser(null)
    }
  }, [props.authFailure, setAccessToken, setRefreshToken, setUser])

  // === Rendering ===

  if (!syncingGameData) {
    // Render page error if user is not signed in
    if (user === null || props.authFailure) {
      return <PageError statusCode={401} />
    }

    // Render page error if game doesn't exist or hasn't started yet
    if (game === null || game.start_date === null) {
      return <PageError statusCode={404} />
    }
  }

  // Render loading spinner if game data is being synchronized
  if (syncingGameData) {
    return (
      <>
        <Head>
          <title>Loading... | Republic of Rome Online</title>
        </Head>
        <main className="h-full p-2">
          <div className="h-full flex flex-col justify-center gap-6 items-center text-lg">
            <span>Synchronizing{game && `: ${game.name}`}</span>
            <CircularProgress size={60} />
          </div>
        </main>
      </>
    )
  }

  return (
    <>
      <Head>
        <title>{`${game!.name} | Republic of Rome Online`}</title>
      </Head>
      <main className="p-2 flex flex-col xl:overflow-auto xl:h-screen bg-neutral-300 dark:bg-neutral-800">
        <div className="flex flex-col gap-2 xl:overflow-auto xl:grow">
          <MetaSection />
          <div className="flex flex-col gap-2 xl:flex-row xl:overflow-auto xl:flex-1">
            <div className="xl:flex-1 xl:max-w-[540px] max-h-[75vh] xl:max-h-none">
              <DetailSection />
            </div>
            <div className="xl:flex-1 xl:grow-[2] bg-neutral-50 dark:bg-neutral-700 rounded shadow overflow-auto">
              <section className="flex flex-col h-[75vh] xl:h-full">
                <div className="border-0 border-b border-solid border-neutral-200 dark:border-neutral-750">
                  <Tabs
                    value={mainTab}
                    onChange={handleMainTabChange}
                    className="px-4"
                  >
                    <Tab label="Factions" />
                    <Tab label="Senators" />
                    <Tab label="Senate" />
                    <Tab label="Warfare" />
                  </Tabs>
                </div>
                {mainTab === 0 && <FactionList />}
                {mainTab === 1 && (
                  <div className="h-full box-border m-4">
                    <SenatorList
                      selectable
                      border
                      mainSenatorListSortState={[
                        mainSenatorListSort,
                        setMainSenatorListSort,
                      ]}
                      mainSenatorListFilterAliveState={[
                        mainSenatorListFilterAlive,
                        setMainSenatorListFilterAlive,
                      ]}
                      mainSenatorListFilterDeadState={[
                        mainSenatorListFilterDead,
                        setMainSenatorListFilterDead,
                      ]}
                    />
                  </div>
                )}
                {mainTab === 2 && <SenateTab />}
                {mainTab === 3 && <WarfareTab />}
              </section>
            </div>
            <div className="xl:flex-1 xl:max-w-[540px] bg-neutral-50 dark:bg-neutral-700 rounded shadow">
              <section className="flex flex-col h-[75vh] xl:h-full">
                <ProgressSection />
              </section>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}

export default GamePage
