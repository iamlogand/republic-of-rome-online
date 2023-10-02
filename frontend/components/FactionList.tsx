import { useEffect, useState } from 'react'

import Faction from '@/classes/Faction'
import FactionListItem from '@/components/FactionListItem'
import { useGameContext } from '@/contexts/GameContext'
import styles from './FactionList.module.css'
import Collection from '@/classes/Collection'

// List of factions
const FactionList = () => {
  const { allFactions } = useGameContext()

  // State for the sorted factions
  const [sortedFactions, setSortedFactions] = useState<Collection<Faction>>(new Collection<Faction>())

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
        <div className={styles.listItem} role="row" aria-label={`${faction.getName()} Faction`}>
          <FactionListItem faction={faction} />
        </div>
      </div>
    )
  }

  return (
    <div className={styles.listContainer}>
      <div className={styles.list}>
        {sortedFactions.asArray.map(faction => getRow(faction))}
      </div>
    </div>
  )
}

export default FactionList
