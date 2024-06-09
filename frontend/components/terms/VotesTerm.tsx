import Image from "next/image"
import VotesIcon from "@/images/icons/votes.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Votes
const VotesTerm = () => (
  <TermLayout
    title="Votes"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={VotesIcon} height={40} width={40} alt="Votes icon" />
      </Avatar>
    }
    category="Attribute"
  >
    <p>
      <b>Votes</b> is a fluctuating <TermLink name="Senator" /> attribute,
      indicating the maximum number of Votes a Senator can cast in a Proposal,
      excluding Temporary Votes.
    </p>
    <p>
      A Senator&apos;s number of Votes is determined by his{" "}
      <TermLink name="Oratory" /> rating plus his <TermLink name="Knights" />{" "}
      rating.
    </p>
  </TermLayout>
)

export default VotesTerm
