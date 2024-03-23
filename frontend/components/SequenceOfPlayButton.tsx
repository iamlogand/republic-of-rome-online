import { useGameContext } from "@/contexts/GameContext"
import SelectedDetail from "@/types/SelectedDetail"
import EastIcon from "@mui/icons-material/East"
import WestIcon from "@mui/icons-material/West"

interface SequenceOfPlayButtonProps {
  phaseName: string
  relation: "before" | "after"
}

const SequenceOfPlayButton = ({
  phaseName,
  relation,
}: SequenceOfPlayButtonProps) => {
  const { setSelectedDetail } = useGameContext()
  const handleClick = (
    event: React.MouseEvent<HTMLButtonElement, MouseEvent>,
    phaseName: string
  ) => {
    event.preventDefault()
    setSelectedDetail({
      type: "Term",
      name: `${phaseName} Phase`,
    } as SelectedDetail)
  }
  return (
    <button
      onClick={(event: React.MouseEvent<HTMLButtonElement, MouseEvent>) =>
        handleClick(event, phaseName)
      }
      className="group p-2 flex gap-2 items-center text-sm rounded border-none bg-transparent hover:cursor-pointer hover:bg-neutral-200 dark:hover:bg-neutral-750"
    >
      {relation === "before" && <WestIcon />}
      <p>
        Followed by the{" "}
        <span className="text-base underline decoration-[rgba(82,82,82,0.4)] group-hover:decoration-neutral-600 dark:decoration-[rgba(245,245,245,0.4)] dark:group-hover:decoration-neutral-100">
          {phaseName} Phase
        </span>
      </p>
      {relation === "after" && <EastIcon />}
    </button>
  )
}

export default SequenceOfPlayButton
