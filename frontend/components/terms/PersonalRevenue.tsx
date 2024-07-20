import Image from "next/image"
import { Avatar } from "@mui/material"
import TalentsIcon from "@/images/icons/talents.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"

// Description of the game term: Personal Revenue
const PersonalRevenueTerm = () => (
  <TermLayout
    title="Personal Revenue"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={TalentsIcon}
          height={44}
          width={44}
          alt="Talents icon"
        />
      </Avatar>
    }
  >
    <p>
      <b>Personal Revenue</b> is an amount of <TermLink name="Talent" plural />{" "}
      a <TermLink name="Senator" /> earns as regular income during each {" "}
      <TermLink name="Revenue Phase" />.
    </p>
  </TermLayout>
)

export default PersonalRevenueTerm
