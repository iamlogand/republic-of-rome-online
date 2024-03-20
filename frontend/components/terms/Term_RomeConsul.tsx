import Image from "next/image"
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Rome Consul
const RomeConsulTerm = () => (
  <TermLayout
    title="Rome Consul"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={RomeConsulIcon} height={40} width={40} alt={`HRAO Icon`} />
      </Avatar>
    }
    category="Major Office"
    wikipediaPage="Roman_consul"
  >
    <p>
      The Rome Consulship is the second{" "}
      <TermLink
        name="HRAO"
        displayName="Highest Ranking"
      />{" "}
      Office, after the Dictator (if there is one).
    </p>
    <p>
      After being elected, the Rome Consul will become the Presiding Magistrate
      in the Senate. This makes the Rome Consulship one of the most powerful
      offices.
    </p>
    <p>
      The Temporary Rome Consulship is randomly assigned to a{" "}
      <TermLink name="Senator" /> at the start of the game.
    </p>
  </TermLayout>
)

export default RomeConsulTerm
