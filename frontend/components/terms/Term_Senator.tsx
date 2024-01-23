import Image from "next/image"

import SenatorIcon from "@/images/icons/senator.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"

// Description of the game term: Rome Consul
const SenatorTerm = () => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-start gap-4">
        <Avatar sx={{ height: 56, width: 56 }}>
          <Image src={SenatorIcon} height={40} width={40} alt={`HRAO Icon`} />
        </Avatar>
        <div>
          <h5 className="text-sm text-stone-500 dark:text-stone-300">Game Terminology</h5>
          <h4 className="text-xl">
            <b>Senator</b>
          </h4>
        </div>
      </div>
      <div className="flex flex-col gap-3">
        <p>
          A Senator is a member of the Senate that helps to make decisions on behalf of
          the State, primarily by Voting on Proposals and taking Office.
        </p>
        <h5 className="mt-3 font-bold">Attributes</h5>
        <p>Each Senator has three fixed skills:</p>
        <ul className="mt-0 mb-2">
          <li>Military</li>
          <li>Oratory</li>
          <li>Loyalty</li>
        </ul>
        <p>They also have resources that can be gained or lost:</p>
        <ul className="m-0">
          <li>Influence</li>
          <li>Talents</li>
          <li>Popularity</li>
          <li>Knights</li>
          <li>Votes</li>
        </ul>
        <h5 className="mt-3 font-bold">Alignment</h5>
        <p>
          Senators may only take Office or Vote if they are Aligned to a{" "}
          <TermLink name="Faction" />. Unaligned Senators will always Abstain
          from Voting and can&apos;t be assigned an Office.
        </p>
        <p>
          Aligned Senators can grow their Faction by making Persuasion Attempts
          against Unaligned Senators or Senators Aligned to a rival Faction.
        </p>
        <h5 className="mt-3 font-bold">Family</h5>
        <p>
          Most Senators are Family Senators, who are identified by their Family
          name (e.g. “Cornelius”). Each living Family Senator is the current
          leader of their Family. When a Family Senator dies, their Heir may
          return later as an Unaligned Senator.
        </p>
        <h5 className="mt-3 font-bold">Statesmen</h5>
        <p>
          A Statesman is a special type of Senator—a famous historical figure
          with a unique ability. They are identified by their full names (e.g.
          “P. Cornelius Scipio Africanus”). Statesmen can only appear when a
          Faction reveals a Statesman <TermLink name="Secret" />.
        </p>
        <p>
          Statesmen are always Aligned to a Faction, but they are still
          vulnerable to Persuasion Attempts. When they die, they never return.
        </p>
      </div>
    </div>
  )
}

export default SenatorTerm
