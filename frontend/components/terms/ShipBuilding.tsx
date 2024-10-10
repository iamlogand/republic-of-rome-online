import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"
import TalentsAmount from "@/components/TalentsAmount"

// Description of the game term: Ship Building
const ShipBuildingTerm = () => (
  <TermLayout
    title="Ship Building"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={TaxFarmerIcon}
          height={44}
          width={44}
          alt="Ship building icon"
        />
      </Avatar>
    }
    category="Concession"
  >
    <p>
      The <b>Ship Building</b> <TermLink name="Concession" /> represents a{" "}
      <TermLink name="Senator" />
      &apos;s role in overseeing the construction of ships for the Roman navy.
    </p>
    <p>
      The Senator immediately earns <TalentsAmount amount={3} /> for each Fleet
      Raised during the <TermLink name="Senate Phase" />. This also makes him
      liable to a Minor Corruption Prosecution.
    </p>
    <p>
      Ship Building has a chance of being destroyed by a Natural Disaster{" "}
      <TermLink name="Event" />.
    </p>
  </TermLayout>
)

export default ShipBuildingTerm
