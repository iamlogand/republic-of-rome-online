import { useGameContext } from "@/contexts/GameContext"
import WarPortrait from "@/components/WarPortrait"
import { capitalize } from "@mui/material/utils"
import getDiceRollProbability from "@/functions/probability"
import War from "@/classes/War"
import WarStrength from "./WarStrength"

const WarfareTab = () => {
  const { wars, enemyLeaders } = useGameContext()

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
    <div className="m-4 overflow-auto">
      <h3 className="mb-4">Wars</h3>
      <ul className="flex flex-col p-0 gap-4 min-w-[600px]">
        {wars.asArray.map((war) => (
          <li key={war.id} className="list-none flex">
            <div className="w-[560px] flex gap-4 p-2 rounded border border-solid border-stone-300 dark:border-stone-750 bg-stone-100 dark:bg-stone-600">
              <WarPortrait war={war} />
              <div className="w-full flex flex-col">
                <div className="flex items-center justify-between">
                  <h4 className="text-xl">{war.getName()}</h4>
                  {getWarStatus(war)}
                </div>
                <div className="h-full w-full justify-between flex gap-12 mt-2">
                  <div className="h-full flex flex-col justify-between">
                    <div>
                      <p className="text-sm">Strength</p>
                      <p>
                        <WarStrength war={war} type="Land" />
                        {war.navalStrength > 0 && (
                          <span>, <WarStrength war={war} type="Naval" /></span>
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
                  <div className="h-full flex items-end">
                    <div className="flex flex-col gap-1 bg-stone-200 dark:bg-stone-650 px-4 py-2 rounded">
                      {war.fleetSupport > 0 && (
                        <p>
                          Requires <b>{war.fleetSupport}</b> Fleet Support
                        </p>
                      )}
                      <p>
                        <b>{getDiceRollProbability(3, war.disasterNumbers)}</b>{" "}
                        chance of Disaster
                      </p>
                      <p>
                        <b>{getDiceRollProbability(3, war.standoffNumbers)}</b>{" "}
                        chance of Standoff
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
      <ul>
        {enemyLeaders.asArray.map((leader) => (
          <li key={leader.id}>
            {leader.name}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default WarfareTab
