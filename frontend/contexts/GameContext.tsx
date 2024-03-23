import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useCallback,
  useContext,
  useState,
} from "react"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import Collection from "@/classes/Collection"
import Title from "@/classes/Title"
import Game from "@/classes/Game"
import Step from "@/classes/Step"
import SelectedDetail from "@/types/SelectedDetail"
import ActionLog from "@/classes/ActionLog"
import SenatorActionLog from "@/classes/SenatorActionLog"
import Phase from "@/classes/Phase"
import Turn from "@/classes/Turn"
import Secret from "@/classes/Secret"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"
import Action from "@/classes/Action"
import { Dialog } from "@/types/Dialog"

interface GameContextType {
  game: Game | null
  setGame: Dispatch<SetStateAction<Game | null>>
  latestTurn: Turn | null
  setLatestTurn: Dispatch<SetStateAction<Turn | null>>
  latestPhase: Phase | null
  setLatestPhase: Dispatch<SetStateAction<Phase | null>>
  latestStep: Step | null
  setLatestStep: Dispatch<SetStateAction<Step | null>>
  allPlayers: Collection<Player>
  setAllPlayers: Dispatch<SetStateAction<Collection<Player>>>
  allFactions: Collection<Faction>
  setAllFactions: Dispatch<SetStateAction<Collection<Faction>>>
  allSenators: Collection<Senator>
  setAllSenators: Dispatch<SetStateAction<Collection<Senator>>>
  allTitles: Collection<Title>
  setAllTitles: Dispatch<SetStateAction<Collection<Title>>>
  selectedDetail: SelectedDetail | null
  setSelectedDetail: Dispatch<SetStateAction<SelectedDetail | null>>
  actionLogs: Collection<ActionLog>
  setActionLogs: Dispatch<SetStateAction<Collection<ActionLog>>>
  senatorActionLogs: Collection<SenatorActionLog>
  setSenatorActionLogs: Dispatch<SetStateAction<Collection<SenatorActionLog>>>
  senatorDetailTab: number
  setSenatorDetailTab: Dispatch<SetStateAction<number>>
  factionDetailTab: number
  setFactionDetailTab: Dispatch<SetStateAction<number>>
  notifications: Collection<ActionLog>
  setNotifications: Dispatch<SetStateAction<Collection<ActionLog>>>
  allSecrets: Collection<Secret>
  setAllSecrets: Dispatch<SetStateAction<Collection<Secret>>>
  wars: Collection<War>
  setWars: Dispatch<SetStateAction<Collection<War>>>
  enemyLeaders: Collection<EnemyLeader>
  setEnemyLeaders: Dispatch<SetStateAction<Collection<EnemyLeader>>>
  latestActions: Collection<Action>
  setLatestActions: Dispatch<SetStateAction<Collection<Action>>>
  dialog: Dialog
  setDialog: Dispatch<SetStateAction<Dialog>>
  sameSelectionCounter: number
  setSameSelectionCounter: Dispatch<SetStateAction<number>>
}

const GameContext = createContext<GameContextType | null>(null)

export const useGameContext = (): GameContextType => {
  const context = useContext(GameContext)
  if (!context) {
    throw new Error("useGameContext must be used within a GameProvider")
  }
  return context
}

interface GameProviderProps {
  children: ReactNode
}

// Context provider for game-specific state data
export const GameProvider = (props: GameProviderProps): JSX.Element => {
  const [game, setGame] = useState<Game | null>(null)
  const [latestTurn, setLatestTurn] = useState<Turn | null>(null)
  const [latestPhase, setLatestPhase] = useState<Phase | null>(null)
  const [latestStep, setLatestStep] = useState<Step | null>(null)
  const [allPlayers, setAllPlayers] = useState<Collection<Player>>(
    new Collection<Player>()
  )
  const [allFactions, setAllFactions] = useState<Collection<Faction>>(
    new Collection<Faction>()
  )
  const [allSenators, setAllSenators] = useState<Collection<Senator>>(
    new Collection<Senator>()
  )
  const [allTitles, setAllTitles] = useState<Collection<Title>>(
    new Collection<Title>()
  )
  const [selectedDetail, _setSelectedDetail] = useState<SelectedDetail | null>(
    null
  )
  const [actionLogs, setActionLogs] = useState<Collection<ActionLog>>(
    new Collection<ActionLog>()
  )
  const [senatorActionLogs, setSenatorActionLogs] = useState<
    Collection<SenatorActionLog>
  >(new Collection<SenatorActionLog>())
  const [senatorDetailTab, setSenatorDetailTab] = useState<number>(0)
  const [factionDetailTab, setFactionDetailTab] = useState<number>(0)
  const [notifications, setNotifications] = useState<Collection<ActionLog>>(
    new Collection<ActionLog>()
  )
  const [allSecrets, setAllSecrets] = useState<Collection<Secret>>(
    new Collection<Secret>()
  )
  const [wars, setWars] = useState<Collection<War>>(new Collection<War>())
  const [enemyLeaders, setEnemyLeaders] = useState<Collection<EnemyLeader>>(
    new Collection<EnemyLeader>()
  )
  const [latestActions, setLatestActions] = useState<Collection<Action>>(
    new Collection<Action>()
  )
  const [dialog, setDialog] = useState<Dialog>(null)
  const [sameSelectionCounter, setSameSelectionCounter] = useState<number>(0)

  // Wrapper for setSelectedDetail that increments sameSelectionCounter when an already selected item is selected again
  const setSelectedDetail: Dispatch<SetStateAction<SelectedDetail | null>> =
    useCallback(
      (newValue) => {
        if (
          (newValue as SelectedDetail)?.id === selectedDetail?.id &&
          (newValue as SelectedDetail)?.name === selectedDetail?.name
        ) {
          console.log("TEST")
          setSameSelectionCounter((prev) => prev + 1)
        }
        _setSelectedDetail(newValue)
      },
      [selectedDetail]
    )

  return (
    <GameContext.Provider
      value={{
        game,
        setGame,
        latestTurn,
        setLatestTurn,
        latestPhase,
        setLatestPhase,
        latestStep,
        setLatestStep,
        allPlayers,
        setAllPlayers,
        allFactions,
        setAllFactions,
        allSenators,
        setAllSenators,
        allTitles,
        setAllTitles,
        selectedDetail,
        setSelectedDetail,
        actionLogs,
        setActionLogs,
        senatorActionLogs,
        setSenatorActionLogs,
        senatorDetailTab,
        setSenatorDetailTab,
        factionDetailTab,
        setFactionDetailTab,
        notifications,
        setNotifications,
        allSecrets,
        setAllSecrets,
        wars,
        setWars,
        enemyLeaders,
        setEnemyLeaders,
        latestActions,
        setLatestActions,
        dialog,
        setDialog,
        sameSelectionCounter,
        setSameSelectionCounter,
      }}
    >
      {props.children}
    </GameContext.Provider>
  )
}
