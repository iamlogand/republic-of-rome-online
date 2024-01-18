import Image from "next/image"
import { Avatar } from "@mui/material"
import SecretsIcon from "@/images/icons/secrets.svg"
import TermLink from "@/components/TermLink"

// Information about the game term: Secret
const SecretTerm = () => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-start gap-4">
        <Avatar sx={{ height: 56, width: 56 }}>
          <Image src={SecretsIcon} height={44} width={44} alt={`HRAO Icon`} />
        </Avatar>
        <div>
          <h5 className="text-sm text-stone-500">Game Terminology</h5>
          <h4 className="text-xl">
            <b>Secret</b>
          </h4>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <p>
          Secrets are hidden items belonging a <TermLink name="Faction" /> that
          can be revealed to give the Faction an advantage. Each Secret can only
          be revealed once.
        </p>
        <p>There are 3 categories of Secrets:</p>
        <ul className="mt-0 flex flex-col gap-4">
          <li>
            Statesman Secrets can be revealed during the Faction Phase or the
            Forum Phase to immediately bring the named Statesman into the game.
          </li>
          <li>
            Concession Secrets can be revealed during the Faction Phase or the
            Forum Phase to grant a Concession to a chosen Faction Member.
          </li>
          <li>
            Intrigue Secrets can be revealed at various times depending on the
            specific Secret. Their effects are miscellaneous. By far the most
            common of these Secrets is the Tribune, which may be revealed to
            Raise or Veto a Proposal.
          </li>
        </ul>
      </div>
    </div>
  )
}

export default SecretTerm
