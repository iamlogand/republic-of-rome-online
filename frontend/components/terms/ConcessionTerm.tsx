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
      A <b>Concession</b> is a financial advantage that can be assigned to a{" "}
      <TermLink name="Senator" />, enabling him to earn more{" "}
      <TermLink name="Talent" plural />, but it also makes him liable to a Minor
      Corruption Prosecution.
    </p>
    <p>
      Each Concession makes it&apos;s first appearance when a Faction reveals a{" "}
      Concession <TermLink name="Secret" /> to grant the Concession to a Faction
      member.
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
        <TermLink name="Grain" /> (x2)
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
        <TermLink name="Tax Farmer" /> (x6)
      </li>
    </ul>
  </TermLayout>
)

export default ConcessionTerm
