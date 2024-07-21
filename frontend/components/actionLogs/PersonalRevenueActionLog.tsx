import Image from "next/image"
import TalentsIcon from "@/images/icons/talents.svg"
import ActionLog from "@/classes/ActionLog"
import ActionLogLayout from "@/components/ActionLogLayout"
import TermLink from "../TermLink"

interface ActionLogProps {
  notification: ActionLog
}

// ActionLog for when senators earn personal revenue
const PersonalRevenueActionLog = ({ notification }: ActionLogProps) => {
  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={TalentsIcon} alt="Talents icon" width={30} height={30} />
    </div>
  )

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title="Personal Revenue"
    >
      <p>
        <TermLink name="Aligned Senator" plural /> have earned{" "}
        <TermLink name="Personal Revenue" />.
      </p>
    </ActionLogLayout>
  )
}

export default PersonalRevenueActionLog
