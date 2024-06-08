import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"
import HRAOIcon from "@/images/icons/hrao.svg"

// Description of the game term: HRAO
const HraoTerm = () => (
  <TermLayout
    title="HRAO: Highest Ranking Available Official"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={HRAOIcon} height={44} width={44} alt="HRAO icon" />
      </Avatar>
    }
    category="Title"
  >
    <p>
      The <b>HRAO</b> is the Highest Ranking Official in Rome. This{" "}
      <TermLink name="Senator" /> is responsible for opening the Senate. The
      HRAO is typically the Presiding Magistrate.
    </p>
    <h5 className="pt-2 font-bold">Who is the HRAO?</h5>
    <p>
      The order of precedence for determining the HRAO is based on the ranks of
      the Major Offices:
    </p>
    <ol>
      <li>Dictator</li>
      <li>
        <TermLink name="Rome Consul" includeIcon />
      </li>
      <li>Field Consul</li>
      <li>Censor</li>
      <li>Master of Horse</li>
    </ol>
    <p className="pt-2">
      If none of these officials are available, an{" "}
      <TermLink name="Aligned Senator" /> in Rome will be selected based on{" "}
      <TermLink name="Influence" /> (using <TermLink name="Oratory" /> and
      lowest Senator ID to break ties).
    </p>
  </TermLayout>
)

export default HraoTerm
