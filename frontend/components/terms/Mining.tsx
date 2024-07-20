import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"
import TalentsAmount from "@/components/TalentsAmount"

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
      The <b>Mining</b> <TermLink name="Concession" /> represents a{" "}
      <TermLink name="Senator" />
      &apos;s involvement in the regulation Rome&apos;s mining industry.
    </p>
    <p>
      Mining grants the Senator an additional <TalentsAmount amount={3} /> of{" "}
      <TermLink name="Personal Revenue" />. Upon receiving this revenue, the
      Senator becomes liable to a Minor Corruption Prosecution.
    </p>
    <p>Mining has a chance of being destroyed by a Natural Disaster Event.</p>
  </TermLayout>
)

export default MiningTerm
