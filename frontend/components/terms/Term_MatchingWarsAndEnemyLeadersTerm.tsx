import Image from "next/image"
import { Avatar } from "@mui/material"
import WarIcon from "@/images/icons/war.svg"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"
import FullListOfWars from "@/components/FullListOfWars"

// Description of the game term: Matching Wars and Enemy Leaders
const MatchingWarsAndEnemyLeadersTerm = () => (
  <TermLayout
    title="Matching Wars and Enemy Leaders"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={WarIcon} height={44} width={44} alt="War icon" />
      </Avatar>
    }
  >
    <p>
      <b>Matching Wars and Enemy Leaders</b> are sets of two or more{" "}
      <TermLink name="War" plural /> and <TermLink name="Enemy Leader" plural />{" "}
      that are related to each other.
    </p>
    <p>
      During the <TermLink name="Forum Phase" />, the appearance of a new War or
      Enemy Leader causes an <TermLink name="Inactive War" /> or Enemy Leader to
      be activated upon the appearance of a new War or new Enemy Leader of the
      same series of Wars.
    </p>
    <FullListOfWars />
  </TermLayout>
)

export default MatchingWarsAndEnemyLeadersTerm
