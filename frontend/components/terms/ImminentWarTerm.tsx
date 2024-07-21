import Image from "next/image"
import { Avatar } from "@mui/material"
import WarIcon from "@/images/icons/war.svg"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Imminent War
const ImminentWarTerm = () => (
  <TermLayout
    title="Imminent War"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={WarIcon} height={44} width={44} alt="War icon" />
      </Avatar>
    }
  >
    <p>
      An <b>Imminent War</b> is a <TermLink name="War" /> that will attack Rome
      soon, but otherwise behaves the same as an{" "}
      <TermLink name="Inactive War" />.
    </p>
    <p>
      When a new War appears during the <TermLink name="Forum Phase" />, it will
      be Imminent if there is an existing War that{" "}
      <TermLink name="Matching Wars and Enemy Leaders" displayName="Matches" />{" "}
      it.
    </p>
    <h5 className="mt-3 font-bold">Activation</h5>
    <p>
      During the <TermLink name="Mortality Phase" />, one Imminent War (if there
      are any) from each Series of Wars will become{" "}
      <TermLink name="Active War" displayName="Active" />. The order of
      activation is chronological.
    </p>
    <p>Rome can activate an Imminent War by prosecuting it. </p>
  </TermLayout>
)

export default ImminentWarTerm
