import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import SequenceOfPlayDiagram from "@/components/SequenceOfPlayDiagram"
import TermLink from "@/components/TermLink"

// Description of the game term: Senate Phase
const SenatePhaseTerm = () => (
  <TermLayout
    title="Senate Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} width={44} height={44} alt="Time icon" />
      </Avatar>
    }
  >
    <SequenceOfPlayDiagram
      phase="Senate"
      phaseBefore="Population"
      phaseAfter="Combat"
    />
    <p>
      The Senate Phase is the 5th phase of a <TermLink name="Turn" />.
    </p>
  </TermLayout>
)

export default SenatePhaseTerm
