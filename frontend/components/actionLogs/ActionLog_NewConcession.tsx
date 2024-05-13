import Image from "next/image"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "@/components/FactionLink"
import ActionLogLayout from "@/components/ActionLogLayout"
import TermLink from "@/components/TermLink"
import Concession from "@/classes/Concession"
import PersonalTreasuryIcon from "@/images/icons/personalTreasury.svg"

interface ActionLogProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// ActionLog for when a new concession is revealed and assigned to a senator
const NewConcessionActionLog = ({
  notification,
  senatorDetails,
}: ActionLogProps) => {
  const { allFactions, allSenators, allConcessions } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction
    ? allFactions.byId[notification.faction] ?? null
    : null
  const senator: Senator | null = notification.data
    ? allSenators.byId[notification.data.senator] ?? null
    : null
  const concession: Concession | null = notification.data
    ? allConcessions.byId[notification.data.concession] ?? null
    : null

  console.log("Notification", notification)
  console.log("All Concessions", allConcessions)

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image
        src={PersonalTreasuryIcon}
        alt="Talents icon"
        width={30}
        height={30}
      />
    </div>
  )

  if (!senator || !faction || !concession) return null

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title="New Concession"
      faction={faction}
    >
      <p>
        <FactionLink faction={faction} /> has revealed a{" "}
        <TermLink name="Secret" /> to grant <SenatorLink senator={senator} />{" "}
        the {concession.name} Concession.
      </p>
    </ActionLogLayout>
  )
}

export default NewConcessionActionLog
