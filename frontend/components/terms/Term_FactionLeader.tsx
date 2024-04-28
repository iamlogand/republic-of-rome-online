import { Avatar } from "@mui/material"
import FactionIcon from "@/components/FactionIcon"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Faction Leader
const FactionLeaderTerm = () => (
  <TermLayout
    title="Faction Leader"
    category="Title"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <div className="mt-1">
          <FactionIcon size={26} />
        </div>
      </Avatar>
    }
  >
    <p>
      A <b>Faction Leader</b> is a <TermLink name="Senator" /> chosen from among
      a <TermLink name="Faction" displayName="Faction's" /> members to lead the
      Faction. Faction Leaders are immune from Persuasion Attempts, making their{" "}
      <TermLink name="Loyalty" /> ratings irrelevant.
    </p>
    <h5 className="mt-3 font-bold">Succession</h5>
    <p>
      If a Faction Leader dies, his Heir will immediately assume the role of
      Faction Leader. The new Faction Leader will inherit his predecessor&apos;s{" "}
      <TermLink name="Military" />, <TermLink name="Oratory" /> and{" "}
      <TermLink name="Loyalty" />, but not his <TermLink name="Influence" />,
      Talents, Popularity or Knights.
    </p>
  </TermLayout>
)

export default FactionLeaderTerm
