import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import TermLink from "@/components/TermLink"

// Description of the game term: Faction Phase
const FactionPhaseTerm = () => (
  <TermLayout
    title="Faction Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} width={44} height={44} alt="Time icon" />
      </Avatar>
    }
  >
    <p>
      The Faction Phase is a special one-time phase that begins immediately when
      the game starts. The Faction Phase is followed by the{" "}
      <TermLink name="Mortality Phase" />.
    </p>
    <p>
      During this phase, each Faction must select a{" "}
      <TermLink name="Faction Leader" />. They may also reveal their{" "}
      <TermLink name="Statesman" displayName="Statesmen" /> and concession{" "}
      <TermLink name="Secret" plural />.
    </p>
  </TermLayout>
)

export default FactionPhaseTerm
