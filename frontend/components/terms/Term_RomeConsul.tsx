import Image from "next/image"

import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import { Avatar } from "@mui/material"

// Information about the game term: Rome Consul
const RomeConsulTerm = () => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <Avatar className="h-14 w-14 bg-tyrian-100" >
          <Image
            src={RomeConsulIcon}
            height={40}
            width={40}
            alt={`HRAO Icon`}
          />
        </Avatar>
        <h4>
          <b>Rome Consul</b>
        </h4>
      </div>
      <div className="flex flex-col gap-4">
        <p>
          The Rome Consulship is the second highest ranking office, after the
          Dictator (if there is one).
        </p>
        <p>
          After being elected, the Rome Consul will become the Presiding
          Magistrate in the Senate. This makes the Rome Consulship one of the
          most powerful offices.
        </p>
      </div>
    </div>
  )
}

export default RomeConsulTerm
