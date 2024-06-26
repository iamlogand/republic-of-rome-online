import { Avatar } from "@mui/material"
import FactionIcon from "@/components/FactionIcon"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Faction
const FactionTerm = () => (
  <TermLayout
    title="Faction"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <div className="mt-1">
          <FactionIcon size={26} />
        </div>
      </Avatar>
    }
  >
    <p>
      A <b>Faction</b> is a group of <TermLink name="Aligned Senator" plural />{" "}
      controlled by a player. Each Faction can be led by a{" "}
      <TermLink name="Faction Leader" /> chosen from among the Faction members.
    </p>
    <ul className="mt-2 flex flex-col gap-4">
      <li>
        In the Senate, members typically Vote as a block to maximize their
        impact on Proposals.
      </li>
      <li>
        Members can grow the Faction by making Persuasion Attempts against{" "}
        <TermLink name="Unaligned Senator" plural /> or Senators Aligned to a
        rival Faction.
      </li>
      <li>
        Each Faction has a Faction Treasury, which is a hidden pool of{" "}
        <TermLink name="Talent" plural /> primarily used to defend members from
        Persuasion Attempts.
      </li>
      <li>
        Factions can acquire <TermLink name="Secret" plural />, which may be
        revealed and activated to give the Faction an advantage.
      </li>
      <li>Only one Faction can win the game—there are no shared victories.</li>
    </ul>
  </TermLayout>
)

export default FactionTerm
