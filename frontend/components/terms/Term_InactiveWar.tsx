import Image from "next/image"
import { Avatar } from "@mui/material"
import WarIcon from "@/images/icons/war.svg"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Inactive War
const InactiveWarTerm = () => (
  <TermLayout
    title="Inactive War"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={WarIcon} height={44} width={44} alt="War icon" />
      </Avatar>
    }
  >
    <p>
      An <b>Inactive War</b> is a <TermLink name="War" /> that has not yet attacked
      Rome but represents a future threat.
    </p>
    <h5 className="mt-3 font-bold">Activation</h5>
    <p>
      Inactive Wars will develop to an{" "}
      <TermLink name="Active War" displayName="Active" /> state upon the
      appearance of a <TermLink name="Matching Wars and Enemy Leaders" /> during
      the <TermLink name="Forum Phase" />.
    </p>
    <p>Rome can activate an Inactive War by prosecuting it. </p>
  </TermLayout>
)

export default InactiveWarTerm
