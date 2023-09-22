import { Link } from "@mui/material"

import { useGameContext } from '@/contexts/GameContext'
import Faction from "@/classes/Faction"
import SelectedEntity from "@/types/selectedEntity"
import FactionIcon from '@/components/FactionIcon'

interface FactionLinkProps {
  faction: Faction
  includeIcon?: boolean
}

const FactionLink = (props: FactionLinkProps) => {
  const { setSelectedEntity } = useGameContext()

  const handleClick = () => {
    if (props.faction) setSelectedEntity({className: "Faction", id: props.faction.id} as SelectedEntity)
  }

  return (
    <Link component="button" onClick={handleClick} sx={{ verticalAlign: "baseline" }}>
      {props.includeIcon && <span style={{ marginRight: 4 }}><FactionIcon faction={props.faction} size={17} selectable /></span>}
      {props.faction.getName()} Faction
    </Link>
  )
}

export default FactionLink
