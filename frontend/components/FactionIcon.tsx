import Faction from "@/classes/Faction"
import SelectedDetail from "@/types/selectedDetail"
import { useGameContext } from "@/contexts/GameContext"

interface FactionIconProps {
  faction: Faction | null
  size: number
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

  if (faction && faction) {
    const svg = (
      <svg
        className={`overflow-visible mx-px my-[-2px] ${
          muted ? "text-stone-500" : "text-stone-700"
        }`}
        height={size}
        viewBox="0 0 0.9 1"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M0,0 H0.9 V1 L0.45,0.75 L0,1 Z"
          fill={muted ? faction.getColor(300) : faction.getColor(500)}
          stroke="currentColor"
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    )

    const svgInsideButton = (
      <button
        onClick={handleClick}
        className="cursor-pointer border-0 p-0 bg-transparent"
      >
        {svg}
      </button>
    )

    return (
      <span className="inline-block align-baseline">
        {selectable ? svgInsideButton : svg}
      </span>
    )
  } else {
    return null
  }
}

export default FactionIcon
