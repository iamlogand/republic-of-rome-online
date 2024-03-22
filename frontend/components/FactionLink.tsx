import { Link } from "@mui/material"

import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import SelectedDetail from "@/types/SelectedDetail"
import FactionIcon from "@/components/FactionIcon"

interface FactionLinkProps {
  faction: Faction
  includeIcon?: boolean
}

const FactionLink = ({ faction, includeIcon }: FactionLinkProps) => {
  const { setSelectedDetail } = useGameContext()

  const handleClick = (
    event: React.MouseEvent<HTMLAnchorElement, MouseEvent>
  ) => {
    event.preventDefault()
    if (faction)
      setSelectedDetail({
        type: "Faction",
        id: faction.id,
      } as SelectedDetail)
  }

  const getContent = () => (
    <>
      {includeIcon && (
        <span style={{ marginRight: 4 }}>
          <FactionIcon faction={faction} size={17} />
        </span>
      )}
      {faction.getName()} Faction
    </>
  )

  return (
    <Link href="#" onClick={handleClick} sx={{ verticalAlign: "baseline" }}>
      {getContent()}
    </Link>
  )
}

export default FactionLink
