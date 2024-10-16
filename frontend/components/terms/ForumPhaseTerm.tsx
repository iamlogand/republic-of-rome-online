import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import SequenceOfPlayDiagram from "@/components/SequenceOfPlayDiagram"
import TermLink from "@/components/TermLink"

// Description of the game term: Forum Phase
const ForumPhaseTerm = () => (
  <TermLayout
    title="Forum Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} width={44} height={44} alt="Time icon" />
      </Avatar>
    }
  >
    <SequenceOfPlayDiagram
      phase="Forum"
      phaseBefore="Revenue"
      phaseAfter="Population"
    />
    <p>
      The <b>Forum Phase</b> is the 3rd phase of a <TermLink name="Turn" />.
      During this phase, 6 initiatives must be taken, beginning with the{" "}
      <TermLink name="HRAO" />
      &apos;s <TermLink name="Faction" /> and proceeding in Chromatic Order.
      Once all Factions have taken an initiative, any remaining initiatives are
      Auctioned.
    </p>
    <h5 className="mt-3 font-bold">Initiative Sequence</h5>
    <p>The initiative sequence consists of the following steps:</p>
    <ol className="flex flex-col gap-2">
      <li>
        An <TermLink name="Event" /> occurs
      </li>
      <li>Make a Persuasion Attempt</li>
      <li>Attempt to Attract a Knight or Pressure Knights</li>
      <li>Sponsor Games</li>
      <li>
        Select a <TermLink name="Faction Leader" />
      </li>
    </ol>
  </TermLayout>
)

export default ForumPhaseTerm
