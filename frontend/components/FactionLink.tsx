import { Link } from "@mui/material"

import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import SelectedDetail from "@/types/selectedDetail"
import FactionIcon from "@/components/FactionIcon"

interface FactionLinkProps {
  faction: Faction
  includeIcon?: boolean
}

const FactionLink = (props: FactionLinkProps) => {
  const { setSelectedDetail } = useGameContext()

  const handleClick = () => {
    if (props.faction)
      setSelectedDetail({
        type: "Faction",
        id: props.faction.id,
      } as SelectedDetail)
  }

  return (
    <Link
      onClick={handleClick}
      sx={{ verticalAlign: "baseline", userSelect: "auto", cursor: "pointer" }}
    >
      {props.includeIcon && (
        <span style={{ marginRight: 4 }}>
          <FactionIcon faction={props.faction} size={17} />
        </span>
      )}
      {props.faction.getName()} Faction
    </Link>
  )
}

export default FactionLink
