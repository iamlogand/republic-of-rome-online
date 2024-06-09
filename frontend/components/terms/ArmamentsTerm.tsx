import Image from "next/image"
import { Avatar } from "@mui/material"
import ArmamentsIcon from "@/images/icons/armaments.svg"
import TermLayout from "@/components/TermLayout"

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
      An <b>Armaments</b> Concession is...
    </p>
  </TermLayout>
)

export default ArmamentsTerm
