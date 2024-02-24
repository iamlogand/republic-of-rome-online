import { useGameContext } from "@/contexts/GameContext"
import WarList from "./WarList"
import Collection from "@/classes/Collection"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"
import { List, ListItem, ListSubheader } from "@mui/material"

const WarfareTab = () => {
  const { wars, enemyLeaders } = useGameContext()

  const activeWars = new Collection<War>(
    wars.asArray.filter((war) =>
      ["active", "unprosecuted"].includes(war.status)
    )
  )
  const potentialWars = new Collection<War>(
    wars.asArray.filter((war) => ["inactive", "imminent"].includes(war.status))
  )
  const idleEnemyLeaders = new Collection<EnemyLeader>(
    enemyLeaders.asArray.filter((leader) => leader.currentWar === null)
  )

  return (
    <div className="m-4 overflow-auto border border-solid border-stone-200 dark:border-stone-750 rounded shadow-inner bg-white dark:bg-stone-600">
      <List>
        <ListSubheader>
          <h3 className="text-lg font-semibold py-1 px-4 bg-red-300 dark:bg-red-700 text-red-900 dark:text-white rounded-t-md">Active Wars ({activeWars.allIds.length})</h3>
        </ListSubheader>
        <ListItem>
          <div className="w-full p-2 pb-0">
            {activeWars.allIds.length === 0 ? (
              <p className="mt-1 mb-3 px-2">Rome is not engaged in any Active Wars</p>
            ) : (
              <p className="mt-1 mb-3 px-2">
                Rome is engaged in {activeWars.allIds.length} Active{" "}
                {activeWars.allIds.length > 1 ? "Wars" : "War"}
              </p>
            )}
            <WarList wars={activeWars} />
          </div>
        </ListItem>
        <ListSubheader>
          <h3 className="text-lg font-semibold py-1 px-4 bg-green-300 dark:bg-green-700 text-green-900 dark:text-white rounded-t-md">Potential Wars ({potentialWars.allIds.length})</h3>
        </ListSubheader>
        <ListItem>
          <div className="w-full p-2 pb-0">
            {potentialWars.allIds.length === 0 ? (
              <p className="mt-1 mb-3 px-2">Rome is not facing any Potential Wars</p>
            ) : (
              <p className="mt-1 mb-3 px-2">
                Rome is facing {potentialWars.allIds.length} Potential{" "}
                {potentialWars.allIds.length > 1
                  ? "Wars that have"
                  : "War that has"}{" "}
                not yet started
              </p>
            )}
            <WarList wars={potentialWars} />
          </div>
        </ListItem>
        <ListSubheader>
          <h3 className="text-lg font-semibold py-1 px-4 bg-stone-300 dark:bg-stone-750 dark:text-white rounded-t-md">Idle Leaders ({idleEnemyLeaders.allIds.length})</h3>
        </ListSubheader>
        <ListItem>
          <div className="w-full p-2 pb-0">
            {idleEnemyLeaders.allIds.length === 0 ? (
              <p className="mt-1 mb-3 px-2">No idle enemy leaders</p>
            ) : (
              <ul>
                {idleEnemyLeaders.asArray.map((leader) => (
                  <li key={leader.id}>{leader.name}</li>
                ))}
              </ul>
            )}
          </div>
        </ListItem>
      </List>
    </div>
  )
}

export default WarfareTab
