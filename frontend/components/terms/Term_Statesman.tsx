import Image from "next/image"

import SenatorIcon from "@/images/icons/senator.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"
import FullListOfFamilies from "@/components/FullListOfFamilies"

// Description of the game term: Statesman
const StatesmanTerm = () => (
  <TermLayout
    title="Statesman"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={SenatorIcon} height={40} width={40} alt="Senator icon" />
      </Avatar>
    }
  >
    <p>
      A <TermLink name="Statesman" /> is a special type of{" "}
      <TermLink name="Senator" />
      —a famous historical figure with a unique ability. They are identified by
      their full names (e.g. “P. Cornelius Scipio Africanus”). Statesmen can
      only appear when a Faction reveals a Statesman <TermLink name="Secret" />{" "}
      during the <TermLink name="Faction Phase" /> or{" "}
      <TermLink name="Revolution Phase" />.
    </p>
    <p>
      Statesmen are always{" "}
      <TermLink name="Aligned Senator" displayName="Aligned" /> to a{" "}
      <TermLink name="Faction" />, but they are still vulnerable to Persuasion
      Attempts. When they die, they never return.
    </p>
    <p>
      Each Statesman is associated with one of the 3 Scenarios, and they will
      usually only be found in the Scenario they are associated with.
    </p>
    <FullListOfFamilies />
  </TermLayout>
)

export default StatesmanTerm
