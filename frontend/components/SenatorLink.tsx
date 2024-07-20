import { Link } from "@mui/material"
import chroma from "chroma-js"

import { useGameContext } from "@/contexts/GameContext"
import Senator from "@/classes/Senator"
import SelectedDetail from "@/types/SelectedDetail"
import SenatorSummary from "@/components/entitySummaries/SenatorSummary"
import { Tyrian100, Tyrian600 } from "@/themes/colors"
import { useCookieContext } from "@/contexts/CookieContext"

interface SenatorLinkProps {
  senator: Senator
  hiddenUnderline?: boolean
}

const SenatorLink = ({ senator, hiddenUnderline }: SenatorLinkProps) => {
  const { darkMode } = useCookieContext()
  const { setSelectedDetail, setDialog } = useGameContext()

  const handleClick = (
    event: React.MouseEvent<HTMLAnchorElement, MouseEvent>
  ) => {
    event.preventDefault()
    if (senator) {
      setSelectedDetail({
        type: "Senator",
        id: senator.id,
      } as SelectedDetail)
    }
    setDialog(null)
  }

  return (
    <SenatorSummary senator={senator} inline portrait>
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
        {senator.displayName}
      </Link>
    </SenatorSummary>
  )
}

export default SenatorLink
