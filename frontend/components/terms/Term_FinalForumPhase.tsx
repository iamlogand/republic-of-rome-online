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
      During a <TermLink name="Forum Phase" />, if the final Situation is
      initiated, the phase becomes known as the Final Forum Phase. Once this
      phase is ends, the game is over.
    </p>
    <p>
      The mechanics are the same as a regular Forum Phase, but Persuasion
      Attempts are less likely to succeed.
    </p>
  </TermLayout>
)

export default FinalForumPhaseTerm
