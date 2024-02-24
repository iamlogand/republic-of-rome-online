import Faction from "@/classes/Faction"
import SelectedDetail from "@/types/SelectedDetail"
import { useGameContext } from "@/contexts/GameContext"

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
      className={`overflow-visible mx-px my-[-2px] ${
        muted ? "text-stone-500 dark:text-stone-700" : "text-stone-700 dark:text-black"
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
            : "#ff0000"
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
      <style>
        {
          "@keyframes allColorsAnimation { 0% { fill: #ef4444 } 17% { fill: #eab308 } 33% { fill: #22c55e } 50% { fill: #06b6d4 } 67% { fill: #3b82f6 } 83% { fill: #a855f7 } }"
        }
      </style>
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
}

export default FactionIcon
