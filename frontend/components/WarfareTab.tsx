import { useGameContext } from "@/contexts/GameContext"
import WarList from "./WarList"
import Collection from "@/classes/Collection"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"
import { List, ListItem, ListSubheader } from "@mui/material"
import EnemyLeaderPortrait from "@/components/EnemyLeaderPortrait"

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
          <h3 className="text-lg font-semibold py-1 px-4 bg-red-300 dark:bg-red-700 text-red-900 dark:text-white">
            Active Wars ({activeWars.allIds.length})
          </h3>
        </ListSubheader>
        <ListItem>
          <div className="mt-[-1px] w-full p-2 pb-0 bg-red-50 dark:bg-grayRed-600">
            {activeWars.allIds.length === 0 ? (
              <p className="mt-1 mb-3 px-2">
                Rome is not engaged in any Active Wars
              </p>
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
          <h3 className="text-lg font-semibold py-1 px-4 bg-green-300 dark:bg-green-700 text-green-900 dark:text-white">
            Potential Wars ({potentialWars.allIds.length})
          </h3>
        </ListSubheader>
        <ListItem>
          <div className="mt-[-1px] w-full p-2 pb-0 bg-green-50 dark:bg-grayGreen-600">
            {potentialWars.allIds.length === 0 ? (
              <p className="mt-1 mb-3 px-2">
                Rome is not facing any Potential Wars
              </p>
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
          <h3 className="text-lg font-semibold py-1 px-4 bg-stone-300 dark:bg-stone-700 text-stone-600 dark:text-white">
            Idle Leaders ({idleEnemyLeaders.allIds.length})
          </h3>
        </ListSubheader>
        <ListItem>
          {enemyLeaders.asArray.some(
            (leader) => leader.currentWar === null
          ) && (
            <div className="w-full p-4 flex gap-2">
              {enemyLeaders.asArray.map(
                (leader) =>
                  leader.currentWar === null && (
                    <EnemyLeaderPortrait
                      key={leader.id}
                      enemyLeader={leader}
                      size={80}
                      nameTooltip
                    />
                  )
              )}
            </div>
          )}
        </ListItem>
      </List>
    </div>
  )
}

export default WarfareTab
