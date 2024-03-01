import Image from "next/image"
import { Alert } from "@mui/material"
import SenatorIcon from "@/images/icons/senator.svg"
import ActionLog from "@/classes/ActionLog"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import TermLink from "@/components/TermLink"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "../FactionLink"
import Faction from "@/classes/Faction"

interface NotificationProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// Notification for when a senator dies during the mortality phase
const NewFamilyNotification = ({
  notification,
  senatorDetails,
}: NotificationProps) => {
  const { allFactions, allSenators } = useGameContext()

  // Get notification-specific data
  const newSenator: Senator | null = notification.data
    ? allSenators.byId[notification.data.senator] ?? null
    : null
  const initiatingFaction: Faction | null = notification.data
    ? allFactions.byId[notification.data.initiating_faction] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={SenatorIcon} alt="senator icon" width={30} height={30} />
    </div>
  )

  if (!newSenator || !initiatingFaction) return null

  return (
    <Alert icon={getIcon()}>
      <b>New Family: {newSenator.name}</b>
      <p>
        <SenatorLink senator={newSenator} /> {senatorDetails ? "" : "has "}
        joined the Senate as an Unaligned <TermLink name="Senator" />.{" "}
        <i>
          Situation initiated by <FactionLink faction={initiatingFaction} />
        </i>
        .
      </p>
    </Alert>
  )
}

export default NewFamilyNotification
