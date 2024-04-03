import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TalentsIcon from "@/images/icons/talents.svg"
import SequenceOfPlayDiagram from "@/components/SequenceOfPlayDiagram"
import TermLink from "@/components/TermLink"

// Description of the game term: Revenue Phase
const RevenuePhaseTerm = () => (
  <TermLayout
    title="Revenue Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TalentsIcon} width={44} height={44} alt="Talents icon" />
      </Avatar>
    }
  >
    <SequenceOfPlayDiagram
      phase="Revenue"
      phaseBefore="Mortality"
      phaseAfter="Forum"
    />
    <p>
      The Revenue Phase is the 2nd phase of a <TermLink name="Turn" />. During this phase, <TermLink name="Aligned Senators" /> earn Personal Revenue.
    </p>
  </TermLayout>
)

export default RevenuePhaseTerm
