import Image from "next/image"

import SenatorIcon from "@/images/icons/senator.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"
import FullListOfFamilies from "@/components/FullListOfFamilies"

// Description of the game term: Senator
const SenatorTerm = () => (
  <TermLayout
    title="Senator"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={SenatorIcon} height={40} width={40} alt="Senator icon" />
      </Avatar>
    }
  >
    <p>
      A <b>Senator</b> is a member of the Roman Senate that helps to make
      decisions on behalf of the State, primarily by Voting on Proposals and
      taking Office.
    </p>
    <h5 className="mt-3 font-bold">Attributes</h5>
    <p>
      Senators have 3 fixed attributes: <TermLink name="Military" />,{" "}
      <TermLink name="Oratory" /> and <TermLink name="Loyalty" />. They also
      have fluctuating attributes in the form of <TermLink name="Influence" />,{" "}
      <TermLink name="Popularity" /> and <TermLink name="Knights" />; as well as
      a <TermLink name="Personal Treasury" /> of{" "}
      <TermLink name="Talent" plural />.
    </p>
    <p>
      Each Senator possesses a number of <TermLink name="Votes" /> in the
      Senate, which is determined by his Oratory rating plus his Knights rating.
    </p>
    <h5 className="mt-3 font-bold">Alignment</h5>
    <p>
      Senators may only collect <TermLink name="Personal Revenue" />, Vote or
      hold Office if they are{" "}
      <TermLink name="Aligned Senator" displayName="Aligned" /> to a{" "}
      <TermLink name="Faction" />. <TermLink name="Unaligned Senator" plural />{" "}
      cannot do these things.
    </p>
    <p>
      Aligned Senators can grow their Faction by making Persuasion Attempts
      against Unaligned Senators or Senators Aligned to a rival Faction.
    </p>
    <h5 className="mt-3 font-bold">Family</h5>
    <p>
      Most Senators are Family Senators, who are identified by their{" "}
      <TermLink name="Family" /> names (e.g. “Cornelius”). Each living Family
      Senator is the current leader of his Family. When a Family Senator dies,
      his Heir may return later as an Unaligned Senator.
    </p>
    <h5 className="mt-3 font-bold">Statesmen</h5>
    <p>
      A <TermLink name="Statesman" /> is a special type of Senator—a famous
      historical figure with a unique ability. They are identified by their full
      names (e.g. “P. Cornelius Scipio Africanus”). Statesmen can only appear
      when a Faction reveals a Statesman <TermLink name="Secret" />.
    </p>
    <FullListOfFamilies />
  </TermLayout>
)

export default SenatorTerm
