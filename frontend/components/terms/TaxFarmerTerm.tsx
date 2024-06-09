import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"
import EraItem from "@/components/EraItem"

// Description of the game term: Tax Farmer
const TaxFarmerTerm = () => (
  <TermLayout
    title="Tax Farmer"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={TaxFarmerIcon}
          height={44}
          width={44}
          alt="Tax Farmer icon"
        />
      </Avatar>
    }
    category="Concession"
    wikipediaPage="Farm_(revenue_leasing)"
  >
    <p>
      A <b>Tax Farmer</b> is a type of <TermLink name="Concession" /> that
      represents a <TermLink name="Senator" />
      &apos;s association with private tax collection operations in a
      designated region of Italy.
    </p>
    <p>
      Each Tax Farmer grants the Senator an additional 2{" "}
      <TermLink name="Talent" plural /> of <TermLink name="Personal Revenue" />.
      Upon receiving this additional revenue, the Senator becomes liable to a
      Minor Corruption Prosecution.
    </p>
    <h5 className="mt-3 font-bold">Tax Farmer Regions</h5>
    <ul>
      <li>Latium</li>
      <li>Etruria</li>
      <li>Samnium</li>
      <li>Campania</li>
      <li>Apulia</li>
      <li>Lucania</li>
    </ul>
    <h5 className="mt-3 font-bold">Destruction</h5>
    <p>
      Tax Farmers have a chance of being destroyed by some{" "}
      <TermLink name="Active War" plural /> and{" "}
      <TermLink name="Enemy Leader" plural />:
    </p>
    <ul>
      <EraItem
        era="E"
        name={
          <>
            2<sup>nd</sup> Punic War
          </>
        }
        listItem
      />
      <EraItem era="E" name={<i>Hannibal (Enemy Leader)</i>} listItem />
      <EraItem era="L" name="Gladiator Revolt" listItem />
      <EraItem era="L" name={<i>Spartacus (Enemy Leader)</i>} listItem />
    </ul>
  </TermLayout>
)

export default TaxFarmerTerm
