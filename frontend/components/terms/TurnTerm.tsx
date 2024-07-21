import Image from "next/image"
import { Avatar } from "@mui/material"
import TermLayout from "@/components/TermLayout"
import TimeIcon from "@/images/icons/time.svg"
import TermLink from "../TermLink"

// Description of the game term: Turn
const TurnTerm = () => (
  <TermLayout
    title="Turn"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={TimeIcon} width={44} height={44} alt="Time icon" />
      </Avatar>
    }
  >
    <p>
      Republic of Rome is played in a series of <b>Turns</b>. Each turn is
      composed of 7 phases:
    </p>
    <ol>
      <li>
        <TermLink name="Mortality Phase" />
      </li>
      <li>
        <TermLink name="Revenue Phase" />
      </li>
      <li>
        <TermLink name="Forum Phase" />
      </li>
      <li>
        <TermLink name="Population Phase" />
      </li>
      <li>
        <TermLink name="Senate Phase" />
      </li>
      <li>
        <TermLink name="Combat Phase" />
      </li>
      <li>
        <TermLink name="Revolution Phase" />
      </li>
    </ol>
    <p>
      At the beginning of the game, there is the special one-time phase called
      the <TermLink name="Faction Phase" />.
    </p>
  </TermLayout>
)

export default TurnTerm
