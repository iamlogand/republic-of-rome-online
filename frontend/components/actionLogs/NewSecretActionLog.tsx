import Image from "next/image"
import SecretsIcon from "@/images/icons/secrets.svg"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import TermLink from "@/components/TermLink"
import FactionLink from "../FactionLink"
import Faction from "@/classes/Faction"
import ActionLogLayout from "@/components/ActionLogLayout"

interface ActionLogProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// ActionLog for when a secret is gained
const NewSecretActionLog = ({ notification }: ActionLogProps) => {
  const { allFactions } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction
    ? allFactions.byId[notification.faction] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={SecretsIcon} alt="Secrets icon" width={30} height={30} />
    </div>
  )

  if (!faction) return null

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title="New Secret"
      faction={faction}
    >
      <p>
        <FactionLink faction={faction} /> has gained a new{" "}
        <TermLink name="Secret" />.
      </p>
    </ActionLogLayout>
  )
}

export default NewSecretActionLog
