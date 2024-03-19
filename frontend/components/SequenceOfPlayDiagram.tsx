import EastIcon from "@mui/icons-material/East"
import WestIcon from "@mui/icons-material/West"
import TermLink from "@/components/TermLink"

interface SequenceOfPlayDiagramProps {
  phase: string
  phaseBefore: string
  phaseAfter: string
}

const SequenceOfPlayDiagram = ({
  phase,
  phaseBefore,
  phaseAfter,
}: SequenceOfPlayDiagramProps) => {
  const phases = [
    "Mortality",
    "Revenue",
    "Forum",
    "Population",
    "Senate",
    "Combat",
    "Revolution",
  ]

  return (
    <div className="p-4 rounded flex flex-col gap-4 items-center bg-neutral-100 dark:bg-neutral-650">
      <div className="flex gap-2 mb-1">
        {phases.map((p, index) => (
          <div
            key={index}
            className={`w-6 h-6 rounded-full flex justify-center items-center font-bold ${
              p === phase
                ? "bg-neutral-800 text-white dark:bg-white dark:text-black"
                : "bg-neutral-300 dark:bg-neutral-750"
            }`}
          >
            {index + 1}
          </div>
        ))}
      </div>
      <div className="flex gap-8 justify-between">
        <div className="flex gap-2 items-center text-sm">
          <WestIcon />
          <p>
            Preceded by the{" "}
            <span className="text-base">
              <TermLink name={`${phaseBefore} Phase`} />
            </span>
          </p>
        </div>
        <div className="flex gap-2 items-center text-sm">
          <p className="text-end">
            Followed by the{" "}
            <span className="text-base">
              <TermLink name={`${phaseAfter} Phase`} />
            </span>
          </p>
          <EastIcon />
        </div>
      </div>
    </div>
  )
}

export default SequenceOfPlayDiagram
