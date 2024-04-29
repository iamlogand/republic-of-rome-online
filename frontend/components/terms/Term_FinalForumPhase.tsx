import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import TermLink from "@/components/TermLink"

// Description of the game term: Final Forum Phase
const FinalForumPhaseTerm = () => (
  <TermLayout
    title="Final Forum Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} width={44} height={44} alt="Time icon" />
      </Avatar>
    }
  >
    <p>
      After playing the game for several Turns, during the{" "}
      <TermLink name="Forum Phase" />, the final Situation will be initiated. At
      that point the Phase becomes known as the <b>Final Forum Phase</b>. The
      mechanics are the same as a regular Forum Phase, but Persuasion Attempts
      are less likely to succeed.
    </p>
    <p>
      At the end of the Final Forum Phase, the <TermLink name="Faction" /> with
      the most combined <TermLink name="Influence" /> wins the game.
    </p>
  </TermLayout>
)

export default FinalForumPhaseTerm
