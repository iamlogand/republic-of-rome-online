import { useEffect, useState } from "react"

import Faction from "@/classes/Faction"
import FactionListItem from "@/components/FactionListItem"
import { useGameContext } from "@/contexts/GameContext"
import Collection from "@/classes/Collection"

// List of factions
const FactionList = () => {
  const { allFactions } = useGameContext()

  // State for the sorted factions
  const [sortedFactions, setSortedFactions] = useState<Collection<Faction>>(
    new Collection<Faction>()
  )

  // Sort the factions
  useEffect(() => {
    // Sort from lowest to highest rank, and non-null ranks before null ranks
    const factions = allFactions.asArray.sort((a, b) => {
      if (a.rank === null && b.rank === null) return 0
      if (a.rank === null) return 1
      if (b.rank === null) return -1
      return a.rank - b.rank
    })

    setSortedFactions(new Collection<Faction>(factions))
  }, [allFactions])

  // Get JSX for each row in the list
  const getRow = (faction: Faction) => {
    return (
      <div key={faction.id}>
        <div
          className="flex"
          role="row"
          aria-label={`${faction.getName()} Faction`}
        >
          <FactionListItem faction={faction} />
        </div>
      </div>
    )
  }

  return (
    <div className="box-border h-full overflow-auto flex flex-col border border-solid border-neutral-200 dark:border-neutral-750 rounded m-4 bg-white dark:bg-neutral-600">
      <div className={`grow flex flex-col 2xl:grow-0 2xl:grid 2xl:grid-cols-2 gap-2 p-2 shadow-inner`}>
        {sortedFactions.asArray.map((faction) => getRow(faction))}
      </div>
    </div>
  )
}

export default FactionList
