import { Avatar } from "@mui/material"
import FactionIcon from "@/components/FactionIcon"
import TermLink from "@/components/TermLink"

// Description of the game term: Faction
const FactionTerm = () => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-start gap-4">
        <Avatar sx={{ height: 56, width: 56 }}>
          <div className="mt-1">
            <FactionIcon size={26} />
          </div>
        </Avatar>
        <div>
          <h5 className="text-sm text-stone-500 dark:text-stone-300">Game Terminology</h5>
          <h4 className="text-xl">
            <b>Faction</b>
          </h4>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <p>
          A Faction is a group of Aligned{" "}
          <TermLink name="Senator" displayName="Senators" /> controlled by a
          Player. Each Faction can be led by a Faction Leader chosen from among
          the Faction Members.
        </p>
        <ul className="mt-2 flex flex-col gap-4">
          <li>
            In the Senate, Members typically Vote as a block to maximize their
            impact on Proposals.
          </li>
          <li>
            Members can grow the Faction by making Persuasion Attempts against
            Unaligned Senators or Senators Aligned to a rival Faction.
          </li>
          <li>
            Each Faction has a Faction Treasury, which is a hidden pool of
            Talents primarily used to defend Members from Persuasion Attempts.
          </li>
          <li>
            Factions can acquire{" "}
            <TermLink name="Secret" displayName="Secrets" />, which may be
            revealed and activated to give the Faction an advantage.
          </li>
          <li>
            Only one Faction can win the game—there are no shared victories.
          </li>
        </ul>
      </div>
    </div>
  )
}

export default FactionTerm
