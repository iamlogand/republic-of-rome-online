import Image from "next/image"
import KnightsIcon from "@/images/icons/knights.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Knights
const KnightsTerm = () => (
  <TermLayout
    title="Knights"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={KnightsIcon} height={40} width={40} alt="Knights icon" />
      </Avatar>
    }
    category="Attribute"
    wikipediaPage="Equites"
  >
    <p>
      <b>Knights</b> is a fluctuating <TermLink name="Senator" /> attribute,
      where each unit signifies a patron-client relationship between the Senator
      and a wealthy member of the equite class.
    </p>
    <p>
      Each Knight provides the Senator with 1 additional{" "}
      <TermLink name="Votes" displayName="Vote" /> and 1 additional{" "}
      <TermLink name="Talent" /> of <TermLink name="Personal Revenue" />.
    </p>
    <h5 className="mt-3 font-bold">Attract or Pressure</h5>
    <p>
      The only way for a Senator to increase their number of Knights is by
      Attracting a Knight.
    </p>
    <p>
      Senators can Pressure Knights to lose their support in exchange for{" "}
      Talents, sacrificing long term Votes and Personal Revenue in exchange for
      immediate gain of Talents. Knights can never fall below 0.
    </p>
  </TermLayout>
)

export default KnightsTerm
