import Image from "next/image"
import { Avatar } from "@mui/material"
import ArmamentsIcon from "@/images/icons/armaments.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"

// Description of the game term: Armaments
const ArmamentsTerm = () => (
  <TermLayout
    title="Armaments"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={ArmamentsIcon}
          height={44}
          width={44}
          alt="Armaments icon"
        />
      </Avatar>
    }
    category="Concession"
  >
    <p>
      The <b>Armaments</b> <TermLink name="Concession" /> represents a{" "}
      <TermLink name="Senator" />
      &apos;s role in overseeing the production of weapons and armor for the Roman
      military.
    </p>
    <p>
      The Senator immediately earns 2 <TermLink name="Talent" plural /> for each
      Legion Raised during the <TermLink name="Senate Phase" />. This also makes
      him liable to a Minor Corruption Prosecution.
    </p>
    <p>
      Armaments has a chance of being destroyed by a Natural Disaster Event.
    </p>
  </TermLayout>
)

export default ArmamentsTerm
