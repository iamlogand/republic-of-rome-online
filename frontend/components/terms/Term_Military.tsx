import Image from "next/image"
import MilitaryIcon from "@/images/icons/military.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Military
const MilitaryTerm = () => (
  <TermLayout
    title="Military"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={MilitaryIcon} height={38} width={38} alt="Military icon" />
      </Avatar>
    }
    category="attribute"
  >
    <p>
      <b>Military</b> is a fixed <TermLink name="Senator" /> attribute that represents
      a Senator&apos;s ability as a Commander. Senators with a higher Military
      rating are more likely to win Battles.
    </p>
    <p>
      Military can range from terrible (1) to brilliant (6). Most Senators have
      poor (2) or average (3) ratings.
    </p>
  </TermLayout>
)

export default MilitaryTerm
