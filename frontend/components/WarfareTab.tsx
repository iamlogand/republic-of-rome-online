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
    <div className="m-4 overflow-auto border border-solid border-neutral-200 dark:border-neutral-750 rounded shadow-inner bg-white dark:bg-neutral-600">
      <List>
        <ListSubheader>
          <h3 className="text-lg font-semibold py-1 px-4 bg-red-200 dark:bg-red-800 text-red-900 dark:text-white">
            Active Wars {activeWars.allIds.length > 0 && <span>({activeWars.allIds.length})</span>}
          </h3>
        </ListSubheader>
        <ListItem>
          <div className="mt-[-1px] w-full p-2 pb-1 bg-red-50 dark:bg-grayRed-600">
            {activeWars.allIds.length === 0 ? (
              <p className="mt-1 mb-3 px-2">
                Rome is not engaged in any Active Wars.
              </p>
            ) : (
              <p className="mt-1 mb-3 px-2">
                Rome is engaged in {activeWars.allIds.length} Active{" "}
                {activeWars.allIds.length > 1 ? "Wars" : "War"}.
              </p>
            )}
            <WarList wars={activeWars} />
          </div>
        </ListItem>
        <ListSubheader>
          <h3 className="text-lg font-semibold py-1 px-4 bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-white">
            Potential Wars {potentialWars.allIds.length > 0 && <span>({potentialWars.allIds.length})</span>}
          </h3>
        </ListSubheader>
        <ListItem>
          <div className="mt-[-1px] w-full p-2 pb-1 bg-blue-50 dark:bg-grayBlue-600">
            {potentialWars.allIds.length === 0 ? (
              <p className="mt-1 mb-3 px-2">
                Rome is not facing any Potential Wars.
              </p>
            ) : (
              <p className="mt-1 mb-3 px-2">
                Rome is facing {potentialWars.allIds.length} Potential{" "}
                {potentialWars.allIds.length > 1
                  ? "Wars that have"
                  : "War that has"}{" "}
                not yet started.
              </p>
            )}
            <WarList wars={potentialWars} />
          </div>
        </ListItem>
        <ListSubheader>
          <h3 className="text-lg font-semibold py-1 px-4 bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-white">
            Idle Leaders {idleEnemyLeaders.allIds.length > 0 && <span>({idleEnemyLeaders.allIds.length})</span>}
          </h3>
        </ListSubheader>
        <ListItem>
          <div className="w-full p-2 pb-1 bg-blue-50 dark:bg-grayBlue-600">
            {enemyLeaders.asArray.some(
              (leader) => leader.currentWar === null
            ) ? (
              <>
                <p className="mt-1 mb-3 px-2">
                  There{" "}
                  {idleEnemyLeaders.allIds.length > 1 ? (
                    <span>
                      are {idleEnemyLeaders.allIds.length} Enemy Leaders
                    </span>
                  ) : (
                    <span>is 1 Enemy Leader</span>
                  )}{" "}
                  who is currently idle but prepared to engage in a Matching War if one appears.
                </p>
                <div className="px-2 pb-4 flex gap-2">
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
              </>
            ) : (
              <p className="mt-1 mb-3 px-2">There are no idle Enemy Leaders.</p>
            )}
          </div>
        </ListItem>
      </List>
    </div>
  )
}

export default WarfareTab
