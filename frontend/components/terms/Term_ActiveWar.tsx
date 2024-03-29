import Image from "next/image"
import { Avatar } from "@mui/material"
import WarIcon from "@/images/icons/war.svg"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Active War
const ActiveWarTerm = () => (
  <TermLayout
    title="Active War"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={WarIcon} height={44} width={44} alt="War icon" />
      </Avatar>
    }
  >
    <p>
      An Active War is a <TermLink name="War" /> that is currently attacking
      Rome. A critical threat posed by Active Wars is their ability to defeat
      Rome, causing all players to lose, if 4 or more of them remain undefeated
      at the end of the <TermLink name="Combat Phase" />.
    </p>
    <p>
      An Active War that Rome doesn't engage in Battle against during the Combat
      Phase becomes known as an Unprosecuted War.
    </p>
    <h5 className="mt-3 font-bold">Negative Effects</h5>
    <p>
      During the <TermLink name="Revenue Phase" />, the State Treasury loses 20
      Talents for each Active War. During the{" "}
      <TermLink name="Population Phase" />, Rome's Unrest Level increases by 1
      for each Unprosecuted War.
    </p>
  </TermLayout>
)

export default ActiveWarTerm
