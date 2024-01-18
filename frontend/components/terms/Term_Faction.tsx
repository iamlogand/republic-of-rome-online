import { Avatar } from "@mui/material"
import FactionIcon from "@/components/FactionIcon"

// Information about the game term: Faction
const FactionTerm = () => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <Avatar sx={{ height: 56, width: 56 }}>
          <div className="mt-1">
            <FactionIcon size={26} />
          </div>
        </Avatar>
        <h4>
          <b>Faction</b> (Political Entity)
        </h4>
      </div>
      <div className="flex flex-col gap-4">
        <p>
          A Faction is a group of Aligned Senators controlled by a
          Player. Each Faction can be led by a Faction Leader chosen from among
          the Faction Members.
        </p>
        <ul className="mt-2 flex flex-col gap-4">
          <li>
            In the Senate, Members typically Vote as a block to maximize their impact on
            Elections, Proposals and Prosecutions.
          </li>
          <li>
            Members can grow the Faction by making Persuasion Attempts against
            Unaligned Senators or Senators Aligned to a rival Faction.
          </li>
          <li>
            Each Faction has a Faction Treasury, which is a hidden pool of Talents primarily used to defend Senators from Persuasion Attempts.
          </li>
          <li>
            Factions can acquire Secrets, which may be revealed and activated to give the Faction an advantage.
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
