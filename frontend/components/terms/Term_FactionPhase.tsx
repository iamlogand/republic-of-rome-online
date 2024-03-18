import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import TermLink from "@/components/TermLink"

// Description of the game term: Secret
const FactionPhaseTerm = () => (
  <TermLayout
    title="Revenue Phase"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} alt="Time icon" width={44} height={44} />
      </Avatar>
    }
  >
    <p>
      The Faction Phase is a special one-time phase that begins immediately when
      the game starts.
    </p>
    <p>
      During this phase, each Faction must select a{" "}
      <TermLink name="Faction Leader" />. They may also reveal their statesmen
      and concession <TermLink name="Secret" displayName="Secrets" />.
    </p>
  </TermLayout>
)

export default FactionPhaseTerm
