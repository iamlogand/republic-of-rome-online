import Image from "next/image"

import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import { Avatar } from "@mui/material"
import TermLink from "@/components/TermLink"
import ExternalLink from "@/components/ExternalLink"

// Description of the game term: Rome Consul
const RomeConsulTerm = () => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-start gap-4">
        <Avatar sx={{ height: 56, width: 56 }}>
          <Image
            src={RomeConsulIcon}
            height={40}
            width={40}
            alt={`HRAO Icon`}
          />
        </Avatar>
        <div>
          <h5 className="text-sm text-stone-500">Game Terminology</h5>
          <h4 className="text-xl">
            <b>Rome Consul</b> (Major Office)
          </h4>
          <p className="pt-0">
            <ExternalLink href="https://en.wikipedia.org/wiki/Roman_consul">
              Wikipedia
            </ExternalLink>
          </p>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <p>
          The Rome Consulship is the second{" "}
          <TermLink name="HRAO" displayName="Highest Ranking" /> Office, after
          the Dictator (if there is one).
        </p>
        <p>
          After being elected, the Rome Consul will become the Presiding
          Magistrate in the Senate. This makes the Rome Consulship one of the
          most powerful offices.
        </p>
        <p>
          The Temporary Rome Consulship is randomly assigned to a{" "}
          <TermLink name="Senator" /> at the start of the game.
        </p>
      </div>
    </div>
  )
}

export default RomeConsulTerm
