import Image from "next/image"
import OratoryIcon from "@/images/icons/oratory.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: LoyaltyTerm
const LoyaltyTerm = () => (
  <TermLayout
    title="Loyalty"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={OratoryIcon} height={40} width={40} alt="Loyalty icon" />
      </Avatar>
    }
    category="Attribute"
  >
    <p>
      <b>Loyalty</b> is a fixed <TermLink name="Senator" /> attribute that represents a
      Senator&apos;s degree of adherence to the Faction controlling him. In the
      case on an <TermLink name="Unaligned Senator" />, his Loyalty is a
      representation of his willingness to remaining Unaligned.
    </p>
    <p>
      Senators with lower Loyalty ratings are more susceptible to Persuasion
      Attempts. Loyalty is irrelevant for{" "}
      <TermLink name="Faction Leader" plural /> due to their immunity from
      Persuasion Attempts.
    </p>
    <p>
      Loyalty can range from none (0) to high (10). Most Senators have average
      or high ratings.
    </p>
  </TermLayout>
)

export default LoyaltyTerm
