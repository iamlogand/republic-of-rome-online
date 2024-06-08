import Image from "next/image"
import { Avatar } from "@mui/material"
import EnemyLeaderIcon from "@/images/icons/enemyLeader.svg"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"
import FullListOfWars from "@/components/FullListOfWars"

// Description of the game term: Enemy Leader
const EnemyLeaderTerm = () => (
  <TermLayout
    title="Enemy Leader"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={EnemyLeaderIcon} height={44} width={44} alt="War icon" />
      </Avatar>
    }
  >
    <p>
      An <b>Enemy Leader</b> is a historical enemy of Rome with the power to strengthen{" "}
      <TermLink name="War" plural />, making them more difficult to defeat. Some
      have unique abilities. Each Enemy Leader is associated with a specific{" "}
      series of Wars or an individual War.
    </p>
    <p>
      The appearance of a new Enemy Leader is one of several possible Situations
      that can be initiated during the <TermLink name="Forum Phase" />.
    </p>
    <p>
      If there are no{" "}
      <TermLink
        name="Matching Wars and Enemy Leaders"
        displayName="Matching Wars"
      />
      , an Enemy Leader will be idle. However, as soon as a Matching War
      appears, the Enemy Leader will activate and strengthen the War.
    </p>
    <FullListOfWars />
  </TermLayout>
)

export default EnemyLeaderTerm
