import Popover from "@/components/Popover"
import { WarStrengthBreakdown } from "@/helpers/wars"

interface Props {
  label: string
  breakdown: WarStrengthBreakdown
}

const Row = ({ text, value }: { text: string; value: string }) => (
  <div className="flex justify-between gap-6">
    <span>{text}</span>
    <span className="tabular-nums">{value}</span>
  </div>
)

// Shows the strength a war fights at, with a breakdown of the modifiers behind
// it when matching wars (§1.07.332) or enemy leaders (§1.07.342) have changed it
const WarStrength = ({ label, breakdown }: Props) => {
  if (!breakdown.isModified)
    return <span className="tabular-nums">{breakdown.total}</span>

  return (
    <Popover
      className="inline-block"
      triggerClassName="tabular-nums underline decoration-dotted decoration-neutral-400 underline-offset-4"
      trigger={<>{breakdown.total}</>}
    >
      <div className="flex flex-col gap-1">
        <div className="font-semibold">{label}</div>
        <Row text="Base" value={`${breakdown.base}`} />
        {breakdown.multiplier > 1 && (
          <>
            <Row
              text={`${breakdown.matchingWars.length} matching wars (\u00d7${breakdown.multiplier})`}
              value={`+${breakdown.base * (breakdown.multiplier - 1)}`}
            />
            <ul className="flex flex-col">
              {breakdown.matchingWars.map((war) => (
                <li
                  key={war.id}
                  className="ml-6 list-disc text-sm text-neutral-600"
                >
                  {war.name}
                </li>
              ))}
            </ul>
          </>
        )}
        {breakdown.leaders.map((leader) => (
          <Row
            key={leader.id}
            text={leader.name}
            value={`+${leader.strength}`}
          />
        ))}
        <hr className="-mx-4 border-neutral-300" />
        <Row text="Total" value={`${breakdown.total}`} />
      </div>
    </Popover>
  )
}

export default WarStrength
