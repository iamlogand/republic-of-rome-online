import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Harbor Fees
const HarborFeesTerm = () => (
  <TermLayout
    title="Harbor Fees"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TaxFarmerIcon} height={44} width={44} alt="Harbor fees icon" />
      </Avatar>
    }
    category="Concession"
  >
    <p>
      The <b>Harbor Fees</b> is... 
    </p>
  </TermLayout>
)

export default HarborFeesTerm