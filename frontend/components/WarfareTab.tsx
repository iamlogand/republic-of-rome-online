import { useGameContext } from "@/contexts/GameContext"
import WarList from "./WarList"
import Collection from "@/classes/Collection"
import War from "@/classes/War"
import EnemyLeader from "@/classes/EnemyLeader"

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
    <div className="m-4 overflow-auto">
      <h3 className="text-lg font-bold">Active Wars</h3>
      {activeWars.allIds.length === 0 ? (
        <p className="mb-4">Rome is not engaged in any Active Wars.</p>
      ) : (
        <p className="mb-4">
          Rome is engaged in {activeWars.allIds.length} Active{" "}
          {potentialWars.allIds.length > 1 ? "Wars" : "War"}.
        </p>
      )}
      <WarList wars={activeWars} />
      <h3 className="text-lg font-bold">Potential Wars</h3>
      {potentialWars.allIds.length === 0 ? (
        <p className="mb-4">Rome is not facing any Potential Wars.</p>
      ) : (
        <p className="mb-4">
          Rome is facing {potentialWars.allIds.length} Potential{" "}
          {potentialWars.allIds.length > 1 ? "Wars that have" : "War that has"}{" "}
          not yet started.
        </p>
      )}
      <WarList wars={potentialWars} />
      <h3 className="text-lg font-bold">Idle Leaders</h3>
      {idleEnemyLeaders.allIds.length === 0 ? (
        <p className="mb-4">No idle enemy leaders</p>
      ) : (
        <ul>
          {idleEnemyLeaders.asArray.map((leader) => (
            <li key={leader.id}>{leader.name}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default WarfareTab
