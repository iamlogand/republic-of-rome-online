import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import SequenceOfPlayDiagram from "@/components/SequenceOfPlayDiagram"
import TermLink from "@/components/TermLink"

// Description of the game term: Secret
const ForumPhaseTerm = () => (
  <TermLayout
    title="Forum Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} alt="Time icon" width={44} height={44} />
      </Avatar>
    }
  >
    <SequenceOfPlayDiagram
      phase="Forum"
      phaseBefore="Revenue"
      phaseAfter="Population"
    />
    <p>
      The Forum Phase is the 3rd phase of a <TermLink name="Turn" />. During
      this phase, each <TermLink name="Faction" /> must take an Initiative.
    </p>
  </TermLayout>
)

export default ForumPhaseTerm
