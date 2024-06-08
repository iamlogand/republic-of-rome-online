import Image from "next/image"
import TimeIcon from "@/images/icons/time.svg"
import ActionLog from "@/classes/ActionLog"
import ActionLogLayout from "@/components/ActionLogLayout"
import TermLink from "@/components/TermLink"
import Faction from "@/classes/Faction"
import { useGameContext } from "@/contexts/GameContext"
import FactionLink from "@/components/FactionLink"

interface ActionLogProps {
  notification: ActionLog
}

// ActionLog for when a faction wins the game
const FactionWinsActionLog = ({ notification }: ActionLogProps) => {
  const { allFactions } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction
    ? allFactions.byId[notification.faction] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={TimeIcon} alt="Time icon" width={30} height={30} />
    </div>
  )

  if (!faction) return null

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title={`${faction.getName()} Faction Wins`}
      faction={faction}
    >
      <p>
        Rome has survived, but there can only be one winner.{" "}
        <FactionLink faction={faction} /> has won by surpassing all other{" "}
        <TermLink name="Faction" plural /> in Influence.
      </p>
    </ActionLogLayout>
  )
}

export default FactionWinsActionLog
