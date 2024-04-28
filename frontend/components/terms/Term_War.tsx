import Image from "next/image"
import { Avatar } from "@mui/material"
import WarIcon from "@/images/icons/war.svg"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"
import FullListOfWars from "@/components/FullListOfWars"

// Description of the game term: War
const WarTerm = () => (
  <TermLayout
    title="War"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={WarIcon} height={44} width={44} alt="War icon" />
      </Avatar>
    }
  >
    <p>
      A <b>War</b> represents a military threat to Rome. If there are 4 or more{" "}
      <TermLink name="Active War" plural /> at the end of the{" "}
      <TermLink name="Combat Phase" />, Rome is defeated and all players lose.
    </p>
    <p>
      The appearance of a new War is one of several possible Situations that can
      be initiated during the <TermLink name="Forum Phase" />.
    </p>
    <p>
      During the <TermLink name="Senate Phase" />, Rome can raise and deploy
      Forces to prosecute Wars, the outcomes of which are resolved in Battles
      during the Combat Phase.
    </p>
    <h5 className="mt-3 font-bold">Status</h5>
    <p>
      Wars can be in one of three statuses:{" "}
      <TermLink name="Inactive War" displayName="Inactive" />,{" "}
      <TermLink name="Imminent War" displayName="Imminent" /> or{" "}
      <TermLink name="Active War" displayName="Active" />. Inactive and Imminent
      Wars are not yet attacking Rome, but they represent future threats. Active
      Wars are currently attacking Rome.
    </p>
    <h5 className="mt-3 font-bold">Activation</h5>
    <p>
      Some Wars are inherently Active, while others will become Active due to
      the appearance of a <TermLink name="Matching Wars and Enemy Leaders" />.
    </p>
    <p>
      Rome can prosecute Inactive and Imminent Wars, but this will immediately
      activate them.
    </p>
    <FullListOfWars />
  </TermLayout>
)

export default WarTerm
