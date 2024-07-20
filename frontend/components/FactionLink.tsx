import { Link } from "@mui/material"
import chroma from "chroma-js"

import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import SelectedDetail from "@/types/SelectedDetail"
import FactionIcon from "@/components/FactionIcon"
import FactionSummary from "@/components/entitySummaries/FactionSummary"
import FactionName from "@/components/FactionName"
import { Tyrian100, Tyrian600 } from "@/themes/colors"
import { useCookieContext } from "@/contexts/CookieContext"

interface FactionLinkProps {
  faction: Faction
  includeIcon?: boolean
  maxWidth?: number
  hiddenUnderline?: boolean
}

const FactionLink = ({
  faction,
  includeIcon,
  maxWidth,
  hiddenUnderline,
}: FactionLinkProps) => {
  const { darkMode } = useCookieContext()
  const { setSelectedDetail, setDialog } = useGameContext()

  const handleClick = (
    event: React.MouseEvent<HTMLAnchorElement, MouseEvent>
  ) => {
    event.preventDefault()
    if (faction) {
      setSelectedDetail({
        type: "Faction",
        id: faction.id,
      } as SelectedDetail)
    }
    setDialog(null)
  }

  const getContent = () => (
    <>
      {includeIcon && (
        <span style={{ marginRight: 4 }}>
          <FactionIcon faction={faction} size={17} />
        </span>
      )}
      <FactionName faction={faction} maxWidth={maxWidth} />
    </>
  )

  return (
    <FactionSummary faction={faction} inline>
      <Link
        href="#"
        onClick={handleClick}
        sx={{
          verticalAlign: "baseline",
          textDecoration: hiddenUnderline ? "none" : undefined,
          "&:hover": {
            textDecoration: hiddenUnderline
              ? `underline ${chroma(darkMode ? Tyrian100 : Tyrian600).alpha(
                  0.6
                )}`
              : undefined,
          },
        }}
      >
        {maxWidth ? <div className="flex">{getContent()}</div> : getContent()}
      </Link>
    </FactionSummary>
  )
}

export default FactionLink
