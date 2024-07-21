import Image from "next/image"
import { Avatar } from "@mui/material"
import DeadIcon from "@/images/icons/dead.svg"
import TermLayout from "@/components/TermLayout"
import SequenceOfPlayDiagram from "@/components/SequenceOfPlayDiagram"
import TermLink from "@/components/TermLink"

// Description of the game term: Mortality Phase
const MortalityPhaseTerm = () => (
  <TermLayout
    title="Mortality Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={DeadIcon}
          width={40}
          height={40}
          alt="Mortality icon"
          style={{ marginTop: "-4px" }}
        />
      </Avatar>
    }
  >
    <SequenceOfPlayDiagram
      phase="Mortality"
      phaseBefore="Revolution"
      phaseAfter="Revenue"
    />
    <p>
      The <b>Mortality Phase</b> is the 1st phase of a <TermLink name="Turn" />.
      During this phase, one or more <TermLink name="Senator" plural /> may
      randomly die.
    </p>
    <p>
      When a Family Senator dies, his Heir may appear later as an{" "}
      <TermLink name="Unaligned Senator" />. When a Statesman dies, they never
      return.
    </p>
  </TermLayout>
)

export default MortalityPhaseTerm
