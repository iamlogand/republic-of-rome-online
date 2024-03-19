import Image from "next/image"
import { Avatar } from "@mui/material"
import DeadIcon from "@/images/icons/dead.svg"
import TermLayout from "@/components/TermLayout"
import SequenceOfPlayDiagram from "@/components/SequenceOfPlayDiagram"
import TermLink from "@/components/TermLink"

// Description of the game term: Secret
const MortalityPhaseTerm = () => (
  <TermLayout
    title="Mortality Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={DeadIcon}
          alt="Mortality icon"
          width={40}
          height={40}
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
      The Mortality Phase is the 1st phase of a <TermLink name="Turn" />. During
      this phase, one or more <TermLink name="Senator" displayName="Senators" />{" "}
      may randomly die.
    </p>
    <p>
      When a Family Senator dies, their Heir may appear later as an Unaligned
      Senator. When a Statesman dies, they never return.
    </p>
  </TermLayout>
)

export default MortalityPhaseTerm
