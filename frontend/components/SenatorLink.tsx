import { Link } from "@mui/material"

import { useGameContext } from "@/contexts/GameContext"
import Senator from "@/classes/Senator"
import SelectedDetail from "@/types/SelectedDetail"
import SenatorSummary from "@/components/entitySummaries/SenatorSummary"

interface SenatorLinkProps {
  senator: Senator
}

const SenatorLink = ({ senator }: SenatorLinkProps) => {
  const { setSelectedDetail } = useGameContext()

  const handleClick = (
    event: React.MouseEvent<HTMLAnchorElement, MouseEvent>
  ) => {
    event.preventDefault()
    if (senator)
      setSelectedDetail({
        type: "Senator",
        id: senator.id,
      } as SelectedDetail)
  }

  return (
    <SenatorSummary senator={senator} inline portrait>
      <Link href="#" onClick={handleClick} sx={{ verticalAlign: "baseline" }}>
        {senator.displayName}
      </Link>
    </SenatorSummary>
  )
}

export default SenatorLink
