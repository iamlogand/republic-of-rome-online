import Image from "next/image"
import TimeIcon from "@/images/icons/time.svg"
import ActionLog from "@/classes/ActionLog"
import ActionLogLayout from "@/components/ActionLogLayout"
import TermLink from "@/components/TermLink"

interface ActionLogProps {
  notification: ActionLog
}

// ActionLog for when the era ends
const EraEndsActionLog = ({ notification }: ActionLogProps) => {
  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={TimeIcon} alt="Time icon" width={30} height={30} />
    </div>
  )

  return (
    <ActionLogLayout actionLog={notification} icon={getIcon()} title="Era Ends">
      <p>
        The last Situation has been initiated, marking the end of the Early
        Republic Era. Once the <TermLink name="Final Forum Phase" /> is over,
        the game will end, and the <TermLink name="Faction" /> with the most
        <TermLink name="Influence" /> will win.
      </p>
    </ActionLogLayout>
  )
}

export default EraEndsActionLog
