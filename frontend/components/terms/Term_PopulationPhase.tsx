import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import SequenceOfPlayDiagram from "@/components/SequenceOfPlayDiagram"
import TermLink from "@/components/TermLink"

// Description of the game term: Secret
const PopulationPhaseTerm = () => (
  <TermLayout
    title="Population Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} alt="Time icon" width={44} height={44} />
      </Avatar>
    }
  >
    <SequenceOfPlayDiagram
      phase="Population"
      phaseBefore="Forum"
      phaseAfter="Senate"
    />
    <p>
      The Population Phase is the 4th phase of a <TermLink name="Turn" />.
    </p>
  </TermLayout>
)

export default PopulationPhaseTerm
