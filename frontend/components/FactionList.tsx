import { useEffect, useState } from "react"

import Faction from "@/classes/Faction"
import FactionListItem from "@/components/FactionListItem"
import { useGameContext } from "@/contexts/GameContext"
import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import SenatorPortrait from "./SenatorPortrait"
import TermLink from "./TermLink"

// List of factions
const FactionList = () => {
  const { allFactions, allSenators } = useGameContext()

  // State for the sorted factions
  const [sortedFactions, setSortedFactions] = useState<Collection<Faction>>(
    new Collection<Faction>()
  )
  const unalignedSenators = new Collection<Senator>(
    allSenators.asArray
      .filter((s) => s.alive) // Filter by alive
      .filter((s) => s.faction === null) // Filter by unaligned
      .sort((a, b) => a.generation - b.generation) // Sort by generation
      .sort((a, b) => a.name.localeCompare(b.name)) ?? [] // Sort by name
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
    <div className="box-border h-full overflow-auto flex flex-col border border-solid border-neutral-200 dark:border-neutral-750 rounded m-4 bg-white dark:bg-neutral-600 shadow-inner">
      <div className="grow flex flex-col 2xl:grow-0 2xl:grid 2xl:grid-cols-2 gap-2 p-2">
        {sortedFactions.asArray.map((faction) => getRow(faction))}
        <div className="p-2 rounded border border-solid border-neutral-400 dark:border-neutral-800 bg-neutral-200 dark:bg-neutral-700 flex flex-col gap-2">
          <p className="font-bold">
            <TermLink name="Unaligned Senator" plural />
          </p>
          <div className="flex flex-wrap gap-2">
            {unalignedSenators.asArray.map((senator) => (
              <SenatorPortrait
                key={senator.id}
                senator={senator}
                size={80}
                selectable
                summary
                blurryPlaceholder
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default FactionList
