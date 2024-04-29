import Image from "next/image"
import { Avatar } from "@mui/material"
import SecretsIcon from "@/images/icons/secrets.svg"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Secret
const SecretTerm = () => (
  <TermLayout
    title="Secret"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={SecretsIcon} height={44} width={44} alt="Secret icon" />
      </Avatar>
    }
  >
    <p>
      A <b>Secret</b> is a hidden item belonging to a <TermLink name="Faction" /> that can
      be revealed to give the Faction an advantage. Each Secret can only be
      revealed once.
    </p>
    <p>There are 3 categories of Secrets:</p>
    <ul className="mt-0 flex flex-col gap-4">
      <li>
        <span className="font-bold">Statesman Secrets</span> can be revealed
        during the Faction Phase or the Forum Phase to immediately bring the
        named <TermLink name="Statesman" /> into the game.
      </li>
      <li>
        <span className="font-bold">Concession Secrets</span> can be revealed
        during the Faction Phase or the Forum Phase to grant a Concession to a
        chosen Faction Member.
      </li>
      <li>
        <span className="font-bold">Intrigue Secrets</span> can be revealed at
        various times depending on the specific Secret. Their effects are
        miscellaneous. By far the most common of these Secrets is the Tribune,
        which may be revealed to Raise or Veto a Proposal.
      </li>
    </ul>
  </TermLayout>
)

export default SecretTerm
