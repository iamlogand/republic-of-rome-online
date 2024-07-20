import Image from "next/image"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import DeadIcon from "@/images/icons/dead.svg"
import Senator from "@/classes/Senator"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "@/components/FactionLink"
import TermLink from "@/components/TermLink"
import ActionLogLayout from "@/components/ActionLogLayout"

interface ActionLogProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// ActionLog for when a senator dies during the mortality phase
const MortalityActionLog = ({
  notification,
  senatorDetails,
}: ActionLogProps) => {
  const { allFactions, allSenators } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction
    ? allFactions.byId[notification.faction] ?? null
    : null
  const senator: Senator | null = notification.data?.senator
    ? allSenators.byId[notification.data.senator] ?? null
    : null
  const heir: Senator | null = notification.data?.senator
    ? allSenators.byId[notification.data.heir_senator] ?? null
    : null
  const majorOfficeName: string = notification.data?.major_office ?? null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image src={DeadIcon} alt="Mortality icon" width={30} height={30} />
    </div>
  )

  // Get the text for the notification (tense sensitive)
  const getText = () => {
    if (!senator) {
      return (
        <p>
          All <TermLink name="Senator" plural /> have survived the{" "}
          <TermLink name="Mortality Phase" />.
        </p>
      )
    }

    return (
      <p>
        {majorOfficeName || heir ? <span>The</span> : null}
        {majorOfficeName && (
          <span>
            {" "}
            <TermLink name={majorOfficeName} displayName={majorOfficeName} />
          </span>
        )}
        {majorOfficeName && heir ? <span> and</span> : null}
        {heir && faction && (
          <span>
            {" "}
            <FactionLink faction={faction} /> Leader
          </span>
        )}
        {majorOfficeName || heir ? <span>, </span> : null}
        <SenatorLink senator={senator} />
        {!heir && faction && (
          <span>
            {" "}
            of the <FactionLink faction={faction} />
          </span>
        )}
        <span> {!senatorDetails && "has"} passed away.</span>
        {heir && (
          <span>
            {" "}
            His heir <SenatorLink senator={heir} /> {!senatorDetails && "has"}{" "}
            replaced him as <TermLink name="Faction Leader" />.
          </span>
        )}
      </p>
    )
  }

  return (
    <ActionLogLayout
      actionLog={notification}
      icon={getIcon()}
      title={<span>{!senator && "No "}Mortality</span>}
    >
      {getText()}
    </ActionLogLayout>
  )
}

export default MortalityActionLog
