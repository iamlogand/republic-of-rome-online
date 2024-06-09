import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Mining
const MiningTerm = () => (
  <TermLayout
    title="Mining"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TaxFarmerIcon} height={44} width={44} alt="Mining icon" />
      </Avatar>
    }
    category="Concession"
  >
    <p>
      A <b>Mining</b> Concession is... 
    </p>
  </TermLayout>
)

export default MiningTerm
