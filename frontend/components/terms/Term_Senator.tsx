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
      A Senator is a member of the Senate that helps to make decisions on behalf
      of the State, primarily by Voting on Proposals and taking Office.
    </p>
    <h5 className="mt-3 font-bold">Attributes</h5>
    <p>Senators have 3 fixed attributes:</p>
    <ul className="mt-0 mb-2">
      <li><TermLink name="Military" /></li>
      <li><TermLink name="Oratory" /></li>
      <li><TermLink name="Loyalty" /></li>
    </ul>
    <p>They also have 5 variable attributes:</p>
    <ul className="m-0 mb-2">
      <li>Influence</li>
      <li>Talents</li>
      <li>Popularity</li>
      <li>Knights</li>
    </ul>
    <p>Senators have a calculated attribute:</p>
    <ul className="m-0">
      <li>Votes = Oratory + Knights</li>
    </ul>
    <h5 className="mt-3 font-bold">Alignment</h5>
    <p>
      Senators may only collect Personal Revenue, Vote or hold Office if they
      are <TermLink name="Aligned Senator" displayName="Aligned" /> to a{" "}
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
