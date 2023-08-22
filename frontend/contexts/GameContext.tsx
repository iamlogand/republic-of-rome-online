import { Dispatch, ReactNode, SetStateAction, createContext, useContext, useState } from 'react'
import Senator from '@/classes/Senator'
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import Collection from '@/classes/Collection'
import Office from '@/classes/Office'
import Game from '@/classes/Game'
import Step from '@/classes/Step'
import SelectedEntity from '@/types/selectedEntity'

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
  allOffices: Collection<Office>
  setAllOffices: Dispatch<SetStateAction<Collection<Office>>>
  selectedEntity: SelectedEntity | null
  setSelectedEntity: Dispatch<SetStateAction<SelectedEntity | null>>
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
  const [allOffices, setAllOffices] = useState<Collection<Office>>(new Collection<Office>())
  const [selectedEntity, setSelectedEntity] = useState<SelectedEntity | null>(null)

  return (
    <GameContext.Provider value={{
      game, setGame,
      latestStep, setLatestStep,
      allPlayers, setAllPlayers,
      allFactions, setAllFactions,
      allSenators, setAllSenators,
      allOffices, setAllOffices,
      selectedEntity, setSelectedEntity
    }}>
      {props.children}
    </GameContext.Provider>
  )
}
