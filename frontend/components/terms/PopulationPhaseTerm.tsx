import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import SequenceOfPlayDiagram from "@/components/SequenceOfPlayDiagram"
import TermLink from "@/components/TermLink"

// Description of the game term: Population Phase
const PopulationPhaseTerm = () => (
  <TermLayout
    title="Population Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} width={44} height={44} alt="Time icon" />
      </Avatar>
    }
  >
    <SequenceOfPlayDiagram
      phase="Population"
      phaseBefore="Forum"
      phaseAfter="Senate"
    />
    <p>
      The <b>Population Phase</b> is the 4th phase of a <TermLink name="Turn" />
      .
    </p>
  </TermLayout>
)

export default PopulationPhaseTerm
