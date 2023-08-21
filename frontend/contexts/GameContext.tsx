import { Dispatch, ReactNode, SetStateAction, createContext, useContext, useState } from 'react'
import FamilySenator from '@/classes/FamilySenator'
import Collection from '@/classes/Collection'

interface GameContextType {
  allSenators: Collection<FamilySenator>
  setAllSenators: Dispatch<SetStateAction<Collection<FamilySenator>>>
}

const GameContext = createContext<GameContextType | null>(null)

export const useGameContext = (): GameContextType => {
  const context = useContext(GameContext);
if (!context) {
  throw new Error("useGameContext must be used within a GameProvider")
}
return context
}

interface GameProviderProps {
  children: ReactNode
}

export const GameProvider = ( props: GameProviderProps ) => {

  const [allSenators, setAllSenators] = useState<Collection<FamilySenator>>(new Collection<FamilySenator>())

  return (
    <GameContext.Provider value={{ allSenators, setAllSenators }}>
      {props.children}
    </GameContext.Provider>
  )
}
