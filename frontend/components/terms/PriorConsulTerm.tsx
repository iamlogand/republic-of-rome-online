import Image from "next/image"
import { Avatar } from "@mui/material"
import PriorConsulIcon from "@/images/icons/priorConsul.svg"
import TermLink from "@/components/TermLink"
import TermLayout from "@/components/TermLayout"

// Description of the game term: Prior Consul
const PriorConsulTerm = () => (
  <TermLayout
    title="Prior Consul"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={PriorConsulIcon}
          height={44}
          width={44}
          alt="Prior consul icon"
        />
      </Avatar>
    }
    category="Title"
  >
    <p>
      A <b>Prior Consul</b> is an experienced <TermLink name="Senator" /> who
      has served as <TermLink name="Rome Consul" />, Field Consul or Dictator.
    </p>
    <p>
      The title of Prior Consul is held for life unless lost during a
      Prosecution, in which case the Prosecutor will take the Prior Consul title
      from the Accused.
    </p>
    <h5 className="pt-2 font-bold">Becoming Censor</h5>
    <p>
      Eligibility for being elected Censor is exclusively available to Prior
      Consuls without a Major Office. However, if there is only one eligible
      candidate, they will be appointed automatically.
    </p>
    <p>
      If there are no eligible candidates, then any Senators without a Major
      Office can be elected.
    </p>
  </TermLayout>
)

export default PriorConsulTerm
