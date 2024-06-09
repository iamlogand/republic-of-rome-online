import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"

// Description of the game term: Concession
const ConcessionTerm = () => (
  <TermLayout
    title="Concession"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={TaxFarmerIcon}
          height={44}
          width={44}
          alt="Concession icon"
        />
      </Avatar>
    }
  >
    <p>
      A <b>Concession</b> is a financial advantage that can be granted to a{" "}
      <TermLink name="Senator" /> by revealing a <TermLink name="Secret" />.
      Upon earning any <TermLink name="Talent" plural /> from a Concession, the
      Senator becomes liable to a Minor Corruption Prosecution.
    </p>
    <p className="mt-3 font-bold">Concession Types</p>
    <ul>
      <li>
        <TermLink name="Armaments" />
      </li>
      <li>
        <TermLink name="Ship Building" />
      </li>
      <li>
        <TermLink name="Grain" />
      </li>
      <li>
        <TermLink name="Harbor Fees" />
      </li>
      <li>
        <TermLink name="Mining" />
      </li>
      <li>
        <TermLink name="Land Commissioner" />
      </li>
      <li>
        <TermLink name="Tax Farmer" />
      </li>
    </ul>
  </TermLayout>
)

export default ConcessionTerm
