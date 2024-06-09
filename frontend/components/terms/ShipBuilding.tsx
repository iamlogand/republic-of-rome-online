import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Ship Building
const ShipBuildingTerm = () => (
  <TermLayout
    title="Ship Building"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TaxFarmerIcon} height={44} width={44} alt="Ship building icon" />
      </Avatar>
    }
    category="Concession"
  >
    <p>
      The <b>Ship Building</b> is... 
    </p>
  </TermLayout>
)

export default ShipBuildingTerm