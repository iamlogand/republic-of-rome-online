import Image from "next/image"
import PopularityIcon from "@/images/icons/popularity.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Popularity
const PopularityTerm = () => (
  <TermLayout
    title="Popularity"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={PopularityIcon}
          height={42}
          width={42}
          alt="Popularity icon"
        />
      </Avatar>
    }
    category="attribute"
  >
    <p>
      <b>Popularity</b> is a fluctuating <TermLink name="Senator" /> attribute
      that represents a Senator&apos;s reputation among the common people of
      Rome. The highest possible Popularity is +9 (loved), and the lowest is -9
      (hated).
    </p>
    <h5 className="mt-3 font-bold">Effects</h5>
    <ul>
      <li>Better received State of the Republic Speech</li>
      <li>Better results from Popular Appeals</li>
      <li>
        The Popularity of the would-be victim of a caught Assassin affects the
        result of the Popular Appeal in the respective Special Major Prosecution
      </li>
    </ul>
    <h5 className="mt-3 font-bold">Gaining Popularity</h5>
    <ul>
      <li>Sponsor Games</li>
      <li>Sponsor a Land Bill</li>
      <li>Victory in Battle as a Commander</li>
    </ul>

    <h5 className="mt-3 font-bold">Losing Popularity</h5>
    <ul>
      <li>Get convicted in a Minor Prosecution</li>
      <li>Vote against a Proposal for a Land Bill</li>
      <li>Sponsor or Vote for a Repeal of a Land Bill</li>
      <li>Lose Legions in Battle as a Commander</li>
    </ul>
  </TermLayout>
)

export default PopularityTerm
