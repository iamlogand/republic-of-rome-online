import Image from "next/image"
import InfluenceIcon from "@/images/icons/influence.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Influence
const InfluenceTerm = () => (
  <TermLayout
    title="Influence"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={InfluenceIcon}
          height={40}
          width={40}
          alt="Influence icon"
        />
      </Avatar>
    }
    category="Attribute"
    wikipediaPage="Auctoritas"
  >
    <p>
      <b>Influence</b> is a fluctuating <TermLink name="Senator" /> attribute
      that represents a Senator&apos;s prestige in Roman society. Influence can
      never fall below 0.
    </p>
    <h5 className="mt-3 font-bold">Effects</h5>
    <ul>
      <li>Stronger Persuasion Attempts</li>
      <li>
        <TermLink name="HRAO" displayName="Higher Rank" />
      </li>
      <li>Additional Votes if Accused</li>
      <li>Increased Ransom cost at 6 Influence</li>
      <li>Eligible for Consul for Life Election at 21 Influence</li>
      <li>Appointed Consul for Life at 35 Influence</li>
      <li>
        Combined Influence determines the Winning Faction at the end of the{" "}
        <TermLink name="Final Forum Phase" />
      </li>
    </ul>
    <h5 className="mt-3 font-bold">Gaining Influence</h5>
    <ul>
      <li>Gain a Major Office</li>
      <li>Victory in Battle as a Commander</li>
      <li>Make a successful Conviction as a Prosecutor</li>
      <li>Contribute to the State Treasury</li>
      <li>Develop a Province as a Governor</li>
    </ul>
    <h5 className="mt-3 font-bold">Losing Influence</h5>
    <ul>
      <li>Unanimous Defeat of a Proposal</li>
      <li>Get convicted in a Minor Prosecution</li>
      <li>
        <TermLink name="Faction Leader" /> of a caught Assassin
      </li>
    </ul>
  </TermLayout>
)

export default InfluenceTerm
