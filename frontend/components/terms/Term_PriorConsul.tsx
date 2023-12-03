import Image from "next/image"

import PriorConsulIcon from "@/images/icons/priorConsul.svg"
import TermLink from "../TermLink"

// Information about the game term: Prior Consul
const PriorConsulTerm = () => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <div className="h-14 w-14">
          <Image
            src={PriorConsulIcon}
            height={64}
            width={64}
            alt={`HRAO Icon`}
            className="m-[-4px]"
          />
        </div>
        <h4>
          <b>Prior Consul</b> (Title)
        </h4>
      </div>
      <div className="flex flex-col gap-4">
        <p>
          Prior Consuls are experienced Senators who have served as{" "}
          <TermLink name="Rome Consul" />, Field Consul or Dictator.
        </p>
        <p>
          The title of Prior Consul is held for life unless lost during a
          Prosecution, in which case the Prosecutor will take the Prior Consul
          title from the Accused.
        </p>
        <h5 className="pt-2 font-semibold">Becoming Censor</h5>
        <p>
          Eligibility for being elected Censor is exclusively available to Prior
          Consuls without a Major Office. However, if there is only one eligible
          candidate, they will be appointed automatically.
        </p>
        <p>
          If there are no eligible candidates, then any Senators without a Major
          Office can be elected.
        </p>
      </div>
    </div>
  )
}

export default PriorConsulTerm
