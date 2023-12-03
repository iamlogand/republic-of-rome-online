import Image from "next/image"

import HRAOIcon from "@/images/icons/hrao.svg"
import TermLink from "@/components/TermLink"
import { Avatar } from "@mui/material"

// Information about the game term: HRAO
const HraoTerm = () => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <Avatar className="h-14 w-14 bg-tyrian-100">
          <Image
            src={HRAOIcon}
            height={40}
            width={40}
            alt={`HRAO Icon`}
          />
        </Avatar>
        <h4>
          <b>HRAO</b> - <b>H</b>ighest <b>R</b>anking <b>A</b>vailable <b>O</b>
          fficial
        </h4>
      </div>
      <div className="flex flex-col gap-4">
        <p>
          The HRAO is the highest ranking official in Rome. This senator is
          responsible for opening the Senate. The HRAO is typically the
          Presiding Magistrate.
        </p>
        <h5 className="pt-4 font-semibold">Who is the HRAO?</h5>
        <p>The order of precedence for determining the HRAO is:</p>
        <ol>
          <li>Dictator</li>
          <li>
            <TermLink name="Rome Consul" includeIcon />
          </li>
          <li>Field Consul</li>
          <li>Censor</li>
          <li>Master of Horse</li>
        </ol>
        <p className="pt-2">
          If none of these officials are available, an aligned senator in Rome
          will be selected based on Influence (using Oratory and lowest Senator
          ID to break ties).
        </p>
      </div>
    </div>
  )
}

export default HraoTerm
