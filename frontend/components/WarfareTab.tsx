import { useGameContext } from "@/contexts/GameContext"
import WarPortrait from "@/components/WarPortrait"
import { capitalize } from "@mui/material/utils"
import getDiceRollProbability from "@/functions/probability"

const WarfareTab = () => {
  const { wars } = useGameContext()

  return (
    <div className="m-4">
      <h3 className="mb-4">Wars</h3>
      <ul className="flex flex-col p-0">
        {wars.asArray.map((war) => (
          <li key={war.id} className="list-none flex">
            <div className="flex gap-4 p-2 rounded border border-solid border-stone-300 dark:border-stone-750 bg-stone-100 dark:bg-stone-600">
              <WarPortrait war={war} />
              <div className="flex flex-col">
                <div className="flex items-baseline justify-between">
                  <h4 className="text-2xl">{war.getName()}</h4>
                  <p className="pr-2">
                    <b>{capitalize(war.status)}</b>
                  </p>
                </div>
                <div className="h-full flex gap-12 mt-2">
                  <div className="h-full flex flex-col justify-between">
                    <div>
                      <p className="text-sm">Strength</p>
                      <p>
                        <b>{war.landStrength} Land</b>,{" "}
                        <b>{war.landStrength} Naval</b>{" "}
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
                    <div className="flex flex-col gap-1 bg-stone-200 dark:bg-stone-650 px-2 py-1 rounded">
                      <p>
                        Requires <b>{war.fleetSupport}</b> Fleet Support
                      </p>
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
    </div>
  )
}

export default WarfareTab
