import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"

// Description of the game term: Land Commissioner
const LandCommissionerTerm = () => (
  <TermLayout
    title="Land Commissioner"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={TaxFarmerIcon}
          height={44}
          width={44}
          alt="Land commissioner icon"
        />
      </Avatar>
    }
    category="Concession"
  >
    <p>
      The <b>Land Commissioner</b> is a <TermLink name="Concession" /> that
      signifies a <TermLink name="Senator" />
      &apos;s role in the allocation of land when there is at least one Land
      Bill in effect.
    </p>
  </TermLayout>
)

export default LandCommissionerTerm
