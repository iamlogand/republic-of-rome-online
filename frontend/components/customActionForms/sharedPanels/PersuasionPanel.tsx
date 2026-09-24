import NumberInput from "../../NumberInput"

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
        <NumberInput
          label={label}
          value={bribe}
          onChange={clamp}
          min={0}
          max={maxBribe}
        />
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
