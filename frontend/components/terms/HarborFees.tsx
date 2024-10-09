import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"
import TalentsAmount from "@/components/TalentsAmount"

// Description of the game term: Harbor Fees
const HarborFeesTerm = () => (
  <TermLayout
    title="Harbor Fees"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={TaxFarmerIcon}
          height={44}
          width={44}
          alt="Harbor fees icon"
        />
      </Avatar>
    }
    category="Concession"
  >
    <p>
      The <b>Harbor Fees</b> <TermLink name="Concession" /> represents a{" "}
      <TermLink name="Senator" />
      &apos;s involvement in the taxation of goods passing through Roman ports.
    </p>
    <p>
      Harbor Fees grants the Senator an additional <TalentsAmount amount={3} />{" "}
      of <TermLink name="Personal Revenue" />. Upon receiving this revenue, the
      Senator becomes liable to a Minor Corruption Prosecution.
    </p>
    <p>
      Harbor Fees has a chance of being destroyed by a Natural Disaster{" "}
      <TermLink name="Event" />.
    </p>
  </TermLayout>
)

export default HarborFeesTerm
