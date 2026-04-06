function successChance(modifier: number, threshold: number): number {
  let successes = 0
  for (let d1 = 1; d1 <= 6; d1++) {
    for (let d2 = 1; d2 <= 6; d2++) {
      const roll = d1 + d2
      if (roll <= modifier && roll < threshold) successes++
    }
  }
  return successes / 36
}

interface PersuasionPanelProps {
  bribe: number
  setBribe: (n: number) => void
  maxBribe: number
  modifier: number
  threshold: number
  totalBribeDisplay?: number
  label?: string
  alwaysShowBribeInput?: boolean
}

const PersuasionPanel = ({
  bribe,
  setBribe,
  maxBribe,
  modifier,
  threshold,
  label = "Bribe",
  alwaysShowBribeInput = false,
}: PersuasionPanelProps) => {
  const clamp = (value: number) =>
    setBribe(Math.max(0, Math.min(maxBribe, value)))

  const chancePercent = Math.round(successChance(modifier, threshold) * 100)

  return (
    <div className="flex flex-col gap-4">
      {(alwaysShowBribeInput || maxBribe > 0) && (
        <div className="flex w-[350px] flex-col gap-1">
          <label className="font-semibold">{label}</label>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => clamp(bribe - 1)}
                disabled={bribe <= 0}
                className="relative h-6 min-w-6 rounded-full border border-red-600 text-red-600 hover:bg-red-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
              >
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                  &minus;
                </div>
              </button>
              <input
                type="number"
                min={0}
                max={maxBribe}
                value={bribe}
                onChange={(e) => clamp(Number(e.target.value))}
                className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5"
              />
              <button
                type="button"
                onClick={() => clamp(bribe + 1)}
                disabled={bribe >= maxBribe}
                className="relative h-6 min-w-6 rounded-full border border-green-600 text-green-600 hover:bg-green-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
              >
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                  +
                </div>
              </button>
            </div>
            {maxBribe > 0 && (
              <div className="flex w-full items-center justify-center">
                <button
                  type="button"
                  className={`w-10 cursor-default px-2 text-sm ${bribe !== 0 && "text-neutral-400"}`}
                  onClick={() => clamp(0)}
                >
                  0
                </button>
                <input
                  type="range"
                  min={0}
                  max={maxBribe}
                  value={bribe}
                  onChange={(e) => clamp(Number(e.target.value))}
                  className="w-full"
                />
                <button
                  type="button"
                  className={`w-10 cursor-default px-2 text-sm ${bribe !== maxBribe && "text-neutral-400"}`}
                  onClick={() => clamp(maxBribe)}
                >
                  {maxBribe}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
      <div className="flex flex-col gap-2">
        <div>
          <div className="inline-flex max-w-[400px] gap-2 rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
            <p>
              Chance of success:{" "}
              <span className="inline-block">{chancePercent}%</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PersuasionPanel
