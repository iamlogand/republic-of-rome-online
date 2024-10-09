import Image from "next/image"

import SenatorIcon from "@/images/icons/senator.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"
import FullListOfFamilies from "@/components/FullListOfFamilies"

// Description of the game term: Family
const FamilyTerm = () => (
  <TermLayout
    title="Family"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={SenatorIcon} height={40} width={40} alt="Senator icon" />
      </Avatar>
    }
  >
    <p>
      Each <TermLink name="Senator" /> belongs to a specific <b>Family</b>. 30
      Roman families are represented in the game, along with 16{" "}
      <TermLink name="Statesman" displayName="Statesmen" />, each of whom is a
      member of a Family.
    </p>
    <p>
      The appearance of a new Family Senator is one of several possible{" "}
      <TermLink name="Event" plural /> that can occur during the{" "}
      <TermLink name="Forum Phase" />.
    </p>
    <p>
      Each Family Senator is associated with one of the 3 Scenarios. Each
      Scenario features Family Senators associated with that scenario, as well
      as Families from earlier Scenarios.
    </p>
    <FullListOfFamilies />
  </TermLayout>
)

export default FamilyTerm
