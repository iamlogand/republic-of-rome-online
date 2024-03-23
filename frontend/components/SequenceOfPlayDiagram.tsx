import SequenceOfPlayButton from "@/components/SequenceOfPlayButton"

const phases = [
  "Mortality",
  "Revenue",
  "Forum",
  "Population",
  "Senate",
  "Combat",
  "Revolution",
]

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
  return (
    <div className="p-4 rounded flex flex-col gap-2 items-center bg-neutral-100 dark:bg-neutral-650">
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
        <SequenceOfPlayButton phaseName={phaseBefore} relation="before" />
        <SequenceOfPlayButton phaseName={phaseAfter} relation="after" />
      </div>
    </div>
  )
}

export default SequenceOfPlayDiagram
