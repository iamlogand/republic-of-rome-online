import Image from "next/image"
import PersonalTreasuryIcon from "@/images/icons/personalTreasury.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Personal Treasury
const PersonalTreasuryTerm = () => (
  <TermLayout
    title="Personal Treasury"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={PersonalTreasuryIcon}
          height={40}
          width={40}
          alt="Talents icon"
        />
      </Avatar>
    }
  >
    <p>
      A <b>Personal Treasury</b> is an amount of Talents (money) personally held by a{" "}
      <TermLink name="Senator" />. Personal Treasuries can never fall below 0
      Talents. If a Senator dies, the contents of their Personal Treasury is lost.
    </p>
    <p>
      Each Talent in a Senator&apos;s Personal Treasury provides passive
      resistance to Persuasion Attempts, making them harder to persuade.
    </p>
    <h5 className="mt-3 font-bold">Earning Talents</h5>
    <ul>
      <li>
        Earning Personal Revenue, which can be increased by controlling Knights
        and Concessions
      </li>
      <li>Taking Provincial Spoils as a Governor</li>
      <li>Redistributing Talents</li>
      <li>Receiving a Persuasion Attempt Bribe</li>
      <li>Pressuring Knights</li>
    </ul>
    <h5 className="mt-3 font-bold">Spending Talents</h5>
    <ul>
      <li>Contribute to the State Treasury</li>
      <li>Redistributing Talents</li>
      <li>Winning an Initiative Auction</li>
      <li>Sending a Persuasion Attempt Bribe</li>
      <li>Attracting a Knight</li>
      <li>Sponsoring Games</li>
      <li>Buying Temporary Votes</li>
      <li>Ransoming a Captive</li>
      <li>Maintaining Legions as a Rebel</li>
    </ul>
  </TermLayout>
)

export default PersonalTreasuryTerm
