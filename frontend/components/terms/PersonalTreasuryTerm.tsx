import Image from "next/image"
import TalentsIcon from "@/images/icons/talents.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"
import TalentsAmount from "@/components/TalentsAmount"

// Description of the game term: Personal Treasury
const PersonalTreasuryTerm = () => (
  <TermLayout
    title="Personal Treasury"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TalentsIcon} height={44} width={44} alt="Talents icon" />
      </Avatar>
    }
  >
    <p>
      A <b>Personal Treasury</b> is an amount of{" "}
      <TermLink name="Talent" plural /> personally held by a{" "}
      <TermLink name="Senator" />. Personal Treasuries can never fall below{" "}
      <TalentsAmount amount={0} />. If a Senator dies, the contents of their
      Personal Treasury is lost.
    </p>
    <p>
      Each Talent in a Senator&apos;s Personal Treasury provides passive
      resistance to Persuasion Attempts, making him harder to persuade.
    </p>
    <h5 className="mt-3 font-bold">Earning Talents</h5>
    <ul>
      <li>
        Earn <TermLink name="Personal Revenue" />, which can be increased by
        controlling <TermLink name="Knights" /> and{" "}
        <TermLink name="Concession" plural />
      </li>
      <li>Take Provincial Spoils as a Governor</li>
      <li>Redistribute Talents</li>
      <li>Receive a Persuasion Attempt Bribe</li>
      <li>Pressure Knights</li>
    </ul>
    <h5 className="mt-3 font-bold">Spending Talents</h5>
    <ul>
      <li>Contribute to the State Treasury</li>
      <li>Redistribute Talents</li>
      <li>Win an Initiative Auction</li>
      <li>Send a Persuasion Attempt Bribe</li>
      <li>Attract a Knight</li>
      <li>Sponsor Games</li>
      <li>Buy Temporary Votes</li>
      <li>Ransom a Captive</li>
      <li>Maintain Legions as a Rebel</li>
    </ul>
  </TermLayout>
)

export default PersonalTreasuryTerm
