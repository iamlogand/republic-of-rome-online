import Image from "next/image"

import SenatorIcon from "@/images/icons/senator.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Aligned Senator
const AlignedSenatorTerm = () => (
  <TermLayout
    title="Aligned Senator"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={SenatorIcon} height={40} width={40} alt="Senator icon" />
      </Avatar>
    }
  >
    <p>
      An Aligned Senator is a <TermLink name="Senator" /> that is a member of a{" "}
      <TermLink name="Faction" />. Unlike{" "}
      <TermLink name="Unaligned Senator" plural />, they can collect Personal
      Revenue, Vote on Proposals and hold Office.
    </p>
  </TermLayout>
)

export default AlignedSenatorTerm
