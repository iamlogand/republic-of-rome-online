import Image from "next/image"
import { Avatar } from "@mui/material"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import TermLayout from "@/components/TermLayout"
import TermLink from "@/components/TermLink"

// Description of the game term: Event
const HarborFeesTerm = () => (
  <TermLayout
    title="Event"
    icon={
      <Avatar sx={{ height: 56, width: 56 }}>
        <Image
          src={TaxFarmerIcon}
          height={44}
          width={44}
          alt="Random event icon"
        />
      </Avatar>
    }
  >
    <p>
      An <b>Event</b> is a random occurrence that happens at the beginning of a{" "}
      <TermLink name="Faction" displayName="Faction's" /> initiative during the{" "}
      <TermLink name="Forum Phase" />. Only the Fates hold the answers to what
      comes next, but the possibilities are confined to the following:
    </p>
    <h5 className="mt-3 font-bold">Common Events</h5>
    <ul>
      <li>
        New <TermLink name="Enemy Leader" />
      </li>
      <li>
        New <TermLink name="Family" />
      </li>
      <li>
        New <TermLink name="Secret" /> (gained by the initiating Faction)
      </li>
      <li>
        New <TermLink name="War" />
      </li>
    </ul>
    <h5 className="mt-3 font-bold">Rare Events</h5>
    <ul>
      <li>Allied Enthusiasm</li>
      <li>Ally Deserts</li>
      <li>Barbarian Raids</li>
      <li>Enemy Ally Deserts</li>
      <li>Enemy Leader Dies</li>
      <li>Epidemic</li>
      <li>Evil Omens</li>
      <li>Famine</li>
      <li>Internal Disorder</li>
      <li>Manpower Shortage</li>
      <li>Natural Disaster</li>
      <li>New Alliance</li>
      <li>Mob Violence</li>
      <li>Pretender</li>
      <li>Refuge</li>
      <li>Rhodian Alliance</li>
      <li>Storm at Sea</li>
      <li>Trial of Verres</li>
    </ul>
  </TermLayout>
)

export default HarborFeesTerm
