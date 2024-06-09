import Image from "next/image"
import TalentIcon from "@/images/icons/personalTreasury.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Talent
const TalentTerm = () => (
  <TermLayout
    title="Talent"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TalentIcon} height={40} width={40} alt="Talent icon" />
      </Avatar>
    }
    wikipediaPage="Talent_(measurement)"
  >
    <p>
      The <b>Talent</b> is the denomination of Roman currency used in the game.
      Each Talent represents a huge amount of wealth—approximately 75 pounds or
      34 kilograms of gold.
    </p>
    <p>Talents are stored in three types of treasury:</p>
    <ul>
      <li>
        Each <TermLink name="Senator" /> has their own{" "}
        <TermLink name="Personal Treasury" />
      </li>
      <li>
        Each <TermLink name="Faction" /> has a private Faction Treasury
      </li>
      <li>The Roman State owns the State Treasury</li>
    </ul>
  </TermLayout>
)

export default TalentTerm
