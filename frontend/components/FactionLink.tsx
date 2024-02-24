import { Link } from "@mui/material"

import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import SelectedDetail from "@/types/SelectedDetail.temp"
import FactionIcon from "@/components/FactionIcon"

interface FactionLinkProps {
  faction: Faction
  includeIcon?: boolean
}

const FactionLink = ({ faction, includeIcon }: FactionLinkProps) => {
  const { selectedDetail, setSelectedDetail } = useGameContext()

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

  if (selectedDetail?.type === "Faction" && selectedDetail.id === faction.id)
    return <span>{getContent()}</span>

  return (
    <Link href="#" onClick={handleClick} sx={{ verticalAlign: "baseline" }}>
      {getContent()}
    </Link>
  )
}

export default FactionLink
