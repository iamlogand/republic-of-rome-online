import { Dispatch, ReactNode, SetStateAction, createContext, useContext, useState } from 'react'
import Senator from '@/classes/Senator'
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import Collection from '@/classes/Collection'
import Title from '@/classes/Title'
import Game from '@/classes/Game'
import Step from '@/classes/Step'
import SelectedDetail from '@/types/selectedDetail'
import ActionLog from '@/classes/ActionLog'
import SenatorActionLog from '@/classes/SenatorActionLog'

interface GameContextType {
  game: Game | null
  setGame: Dispatch<SetStateAction<Game | null>>
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
export const GameProvider = ( props: GameProviderProps ): JSX.Element => {

  const [game, setGame] = useState<Game | null>(null)
  const [latestStep, setLatestStep] = useState<Step | null>(null)
  const [allPlayers, setAllPlayers] = useState<Collection<Player>>(new Collection<Player>())
  const [allFactions, setAllFactions] = useState<Collection<Faction>>(new Collection<Faction>())
  const [allSenators, setAllSenators] = useState<Collection<Senator>>(new Collection<Senator>())
  const [allTitles, setAllTitles] = useState<Collection<Title>>(new Collection<Title>())
  const [selectedDetail, setSelectedDetail] = useState<SelectedDetail | null>(null)
  const [actionLogs, setActionLogs] = useState<Collection<ActionLog>>(new Collection<ActionLog>())
  const [senatorActionLogs, setSenatorActionLogs] = useState<Collection<SenatorActionLog>>(new Collection<SenatorActionLog>())
  const [senatorDetailTab, setSenatorDetailTab] = useState<number>(0)

  return (
    <GameContext.Provider value={{
      game, setGame,
      latestStep, setLatestStep,
      allPlayers, setAllPlayers,
      allFactions, setAllFactions,
      allSenators, setAllSenators,
      allTitles, setAllTitles,
      selectedDetail, setSelectedDetail,
      actionLogs, setActionLogs,
      senatorActionLogs, setSenatorActionLogs,
      senatorDetailTab, setSenatorDetailTab
    }}>
      {props.children}
    </GameContext.Provider>
  )
}
