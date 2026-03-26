import Senator from "@/classes/Senator"
import { STATESMAN_ABILITIES } from "@/helpers/statesmen"

interface SenatorDisplayProps {
  senator: Senator
}

export const majorOffices = ["Rome Consul", "Field Consul", "Censor"]

const SenatorDisplay = ({ senator }: SenatorDisplayProps) => {
  return (
    <div>
      <div className="flex flex-col gap-x-4 gap-y-2 py-2 pl-3 pr-4 lg:pl-5 lg:pr-6">
        <div className="flex items-baseline justify-between gap-4">
          <div className="flex flex-wrap gap-x-4">
            <span>
              <span className="font-semibold">{senator.displayName}</span>
            </span>
            {senator.titles.length > 0 && (
              <>
                {senator.titles.map((title: string, index: number) => (
                  <div
                    key={index}
                    className={`first-letter:uppercase ${majorOffices.includes(title) && "underline underline-offset-2"}`}
                  >
                    {title}
                  </div>
                ))}
              </>
            )}
            {senator.concessions.length > 0 && (
              <>
                {senator.concessions.map(
                  (concession: string, index: number) => (
                    <div key={index} className="flex items-center gap-1">
                      <span className="text-yellow-900 first-letter:uppercase">
                        {concession}
                      </span>
                      {senator.corruptConcessions.includes(concession) && (
                        <span className="flex text-sm text-red-600">
                          (corrupt)
                        </span>
                      )}
                    </div>
                  ),
                )}
              </>
            )}
            {senator.statusItems.includes("major corrupt") && (
              <div className="flex items-center rounded-full bg-red-100 px-2 py-0.5 text-center text-sm text-red-600">
                Major corrupt
              </div>
            )}
            {senator.statusItems.filter((s) => s !== "major corrupt").length >
              0 && (
              <>
                {senator.statusItems
                  .filter((s) => s !== "major corrupt")
                  .map((status: string, index: number) => (
                    <div
                      key={index}
                      className="flex items-center rounded-full bg-neutral-200 px-2 py-0.5 text-center text-sm text-neutral-600"
                    >
                      <span className="first-letter:uppercase">{status}</span>
                    </div>
                  ))}
              </>
            )}
          </div>
          {senator.location !== "Rome" && <div>In {senator.location}</div>}
        </div>
        {senator.statesmanName && (
          <div className="flex gap-4 text-sm text-neutral-600">
            {senator.family && (
              <span>Supported by the {senator.familyName} family</span>
            )}
            {STATESMAN_ABILITIES[senator.code] && (
              <span>{STATESMAN_ABILITIES[senator.code]}</span>
            )}
          </div>
        )}
        <div className="flex flex-wrap gap-x-4 gap-y-2 text-neutral-600">
          <div>
            <span className="text-sm">Military</span>{" "}
            <span className="inline-block w-3">{senator.military}</span>
          </div>
          <div>
            <span className="text-sm">Oratory</span>{" "}
            <span className="inline-block w-3">{senator.oratory}</span>
          </div>
          <div>
            <span className="text-sm">Loyalty</span>{" "}
            <span className="inline-block w-5">{senator.loyalty}</span>
          </div>
          <div>
            <span className="text-sm">Influence</span>{" "}
            <span className="inline-block w-5">{senator.influence}</span>
          </div>
          <div>
            <span className="text-sm">Popularity</span>{" "}
            <span className="inline-block w-5">{senator.popularity}</span>
          </div>
          <div>
            <span className="text-sm">Knights</span>{" "}
            <span className="inline-block w-3">{senator.knights}</span>
          </div>
          <div>
            <span className="text-sm">Votes</span>{" "}
            <span className="inline-block w-3">{senator.votes}</span>
          </div>
          <div className="w-7" dir="rtl">
            {senator.talents}T
          </div>
        </div>
      </div>
    </div>
  )
}

export default SenatorDisplay
