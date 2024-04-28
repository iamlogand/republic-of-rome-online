import Image from "next/image"

import SenatorIcon from "@/images/icons/senator.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Unaligned Senator
const UnalignedSenatorTerm = () => (
  <TermLayout
    title="Unaligned Senator"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={SenatorIcon} height={40} width={40} alt="Senator icon" />
      </Avatar>
    }
  >
    <p>
      An <b>Unaligned Senator</b> is a <TermLink name="Senator" /> that&apos;s not
      controlled by any particular <TermLink name="Faction" />. Unlike{" "}
      <TermLink name="Aligned Senator" plural />, they cannot collect Personal
      Revenue, Vote on Proposals or hold Office.
    </p>
  </TermLayout>
)

export default UnalignedSenatorTerm
