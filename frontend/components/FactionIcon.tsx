import Faction from "@/classes/Faction"
import SelectedDetail from "@/types/SelectedDetail"
import { useGameContext } from "@/contexts/GameContext"
import FactionSummary from "@/components/entitySummaries/FactionSummary"

interface FactionIconProps {
  size: number
  faction?: Faction | null
  selectable?: boolean
  muted?: boolean
}

// Small flag icon representing a faction, identifiable by color
const FactionIcon = ({
  faction,
  size,
  selectable,
  muted,
}: FactionIconProps) => {
  const { setSelectedDetail } = useGameContext()

  const handleClick = () => {
    if (faction?.id)
      setSelectedDetail({
        type: "Faction",
        id: faction.id,
      } as SelectedDetail)
  }

  const svg = (
    <svg
      className={`overflow-visible mx-0.5 my-[-2px] ${
        muted
          ? "text-neutral-500 dark:text-neutral-700"
          : "text-neutral-700 dark:text-black"
      }`}
      height={size}
      viewBox="0 0 0.9 1"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M0,0 H0.9 V1 L0.45,0.75 L0,1 Z"
        fill={
          faction
            ? muted
              ? faction.getColor(300)
              : faction.getColor(500)
            : "#a3a3a3"
        }
        style={
          faction
            ? {}
            : {
                animation: "allColorsAnimation 30s infinite",
              }
        }
        stroke="currentColor"
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  )


  const svgInsideButton = faction ? (
    <FactionSummary faction={faction} inline>
      <button
        onClick={handleClick}
        className="cursor-pointer border-0 p-0 bg-transparent"
      >
        {svg}
      </button>
    </FactionSummary>
  ) : null

  return (
    <span className="inline-block align-baseline">
      {selectable ? svgInsideButton : svg}
    </span>
  )
}

export default FactionIcon
