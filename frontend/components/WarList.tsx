import Collection from "@/classes/Collection"
import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import WarStrength from "@/components/WarStrength"
import { capitalize } from "@mui/material"
import WarPortrait from "@/components/WarPortrait"
import EnemyLeaderPortrait from "@/components/EnemyLeaderPortrait"
import WarDisasterStandoff from "./WarDisasterStandoff"

interface WarListProps {
  wars: Collection<War>
}

const WarList = ({ wars }: WarListProps) => {
  const { enemyLeaders } = useGameContext()

  // Sort wars by alphabetical order and index
  const sortedWars = wars.asArray
    .sort((a, b) => {
      return a.index - b.index
    })
    .sort((a, b) => {
      return a.getName().localeCompare(b.getName())
    })

  const getWarStatus = (war: War) => {
    switch (war.status) {
      case "inactive":
        return (
          <p className="px-2 py-0.5 rounded-full bg-green-700 text-white">
            {capitalize(war.status)}
          </p>
        )
      case "imminent":
        return (
          <p className="px-2 py-0.5 rounded-full bg-amber-400 text-stone-800">
            {capitalize(war.status)}
          </p>
        )
      case "active":
      case "unprosecuted":
        return (
          <p className="px-2 py-0.5 rounded-full bg-red-600 text-white">
            {capitalize(war.status)}
          </p>
        )
      case "defeated":
        return (
          <p className="px-2 py-0.5 rounded-full bg-stone-500 text-white">
            {capitalize(war.status)}
          </p>
        )
    }
  }

  return (
    <div>
      <ul className="w-full flex flex-col p-0 mb-4 gap-2">
        {sortedWars.map((war) => (
          <li key={war.id} className="list-none flex">
            <div className="w-full flex gap-4 p-2 rounded border border-solid border-stone-300 dark:border-stone-800 bg-stone-100 dark:bg-stone-700">
              <WarPortrait war={war} />
              <div className="w-full flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-xl">{war.getName()}</h4>
                  {getWarStatus(war)}
                </div>
                <div className="flex justify-between items-end gap-4 flex-wrap">
                  <div className="min-w-[50px] flex flex-col justify-between">
                    <div>
                      <p className="text-sm">Strength</p>
                      <p>
                        <WarStrength war={war} type="land" />
                        {war.navalStrength > 0 && (
                          <span>
                            , <WarStrength war={war} type="naval" />
                          </span>
                        )}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm">Spoils</p>
                      <p>
                        <b>{war.spoils} Talents</b>
                      </p>
                    </div>
                  </div>

                  <div className="grow flex justify-end">
                    <div className="flex flex-col gap-1 bg-stone-200 dark:bg-stone-750 px-4 py-2 rounded">
                      {war.fleetSupport > 0 && (
                        <p>
                          Requires <b>{war.fleetSupport}</b> Fleet Support
                        </p>
                      )}
                      <p>
                        <WarDisasterStandoff war={war} type="disaster" />
                      </p>
                      <p>
                        <WarDisasterStandoff war={war} type="standoff" />
                      </p>
                    </div>
                  </div>
                  {enemyLeaders.asArray.some(
                    (leader) => leader.currentWar === war.id
                  ) && (
                    <div className="flex gap-2">
                      {enemyLeaders.asArray.map(
                        (leader) =>
                          leader.currentWar === war.id && (
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
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default WarList
