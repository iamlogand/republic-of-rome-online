import { useGameContext } from "@/contexts/GameContext"
import NotificationList from "@/components/NotificationList"
import ActionsArea from "@/components/ActionsArea"

// Progress section showing who players are waiting for
const ProgressSection = () => {
  const { game } = useGameContext()

  return (
    <div className="box-border h-full px-4 pt-2 pb-4 flex flex-col gap-4">
      <NotificationList />
      {!game?.end_date && <ActionsArea />}
    </div>
  )
}

export default ProgressSection
