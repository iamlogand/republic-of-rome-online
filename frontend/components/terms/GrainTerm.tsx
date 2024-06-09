import Image from "next/image"
import { Avatar } from "@mui/material"
import GrainIcon from "@/images/icons/grain.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"
import EraItem from "@/components/EraItem"

// Description of the game term: Grain
const GrainTerm = () => (
  <TermLayout
    title="Grain"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image src={GrainIcon} height={44} width={44} alt="Grain icon" />
      </Avatar>
    }
    category="Concession"
  >
    <p>
      A <b>Grain</b> <TermLink name="Concession" /> represents a{" "}
      <TermLink name="Senator" />
      &apos;s role in the management of Rome&apos;s grain imports. The two variants are
      the Aegyptian Grain and the Sicilian Grain.
    </p>
    <p>
      Each Grain Concession grants the Senator additional{" "}
      <TermLink name="Personal Revenue" />. Upon receiving this revenue, the
      Senator becomes liable to a Minor Corruption Prosecution.
    </p>
    <p>
      If Rome is experiencing a Famine, the Senator can engage in Famine
      Profiteering, further increasing their Personal Revenue at the expense of
      their <TermLink name="Popularity" />.
    </p>
    <h5 className="mt-3 font-bold">Aegyptian Grain</h5>
    <p>
      Aegyptian Grain grants the Senator an additional 5{" "}
      <TermLink name="Talent" plural /> of Personal Revenue. It&apos;s destroyed
      by the <EraItem era="L" name={<>Alexandrine War</>}></EraItem>.
    </p>
    <h5 className="mt-3 font-bold">Sicilian Grain</h5>
    <p>
      Sicilian Grain grants the Senator an additional 4 Talents of Personal
      Revenue. It&apos;s destroyed by two <TermLink name="Active War" plural />:
    </p>
    <ul>
      <EraItem
        era="M"
        name={
          <>
            1<sup>st</sup> Sicilian Slave Revolt
          </>
        }
        listItem
      ></EraItem>
      <EraItem
        era="M"
        name={
          <>
            2<sup>nd</sup> Sicilian Slave Revolt
          </>
        }
        listItem
      ></EraItem>
    </ul>
  </TermLayout>
)

export default GrainTerm
