import Image from "next/image"
import OratoryIcon from "@/images/icons/oratory.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Oratory
const OratoryTerm = () => (
  <TermLayout
    title="Oratory"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={OratoryIcon} height={40} width={40} alt="Oratory icon" />
      </Avatar>
    }
    category="Attribute"
  >
    <p>
      <b>Oratory</b> is a fixed <TermLink name="Senator" /> attribute that
      represents a Senator&apos;s political skill and eloquence. A
      Senator&apos;s number of <TermLink name="Votes" /> is based on his Oratory
      rating.
    </p>
    <p>
      Oratory can range from terrible (1) to brilliant (6). Most Senators have
      poor (2) or average (3) ratings.
    </p>
  </TermLayout>
)

export default OratoryTerm
