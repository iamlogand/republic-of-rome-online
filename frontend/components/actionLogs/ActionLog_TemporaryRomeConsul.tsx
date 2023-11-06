import Image from "next/image"
import { Alert } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "@/components/FactionLink"
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import styles from "./ActionLog.module.css"
import TermLink from "@/components/TermLink"

interface NotificationProps {
  notification: ActionLog
  senatorDetails?: boolean
}

const TemporaryRomeConsulNotification = ({
  notification,
  senatorDetails,
}: NotificationProps) => {
  const { allFactions, allSenators } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction
    ? allFactions.byId[notification.faction] ?? null
    : null
  const senator: Senator | null = notification.data.senator
    ? allSenators.byId[notification.data.senator] ?? null
    : null

  const getIcon = () => (
    <div className={styles.icon}>
      <Image
        src={RomeConsulIcon}
        alt="Rome Consul icon"
        width={30}
        height={30}
      />
    </div>
  )

  // Get the text for the notification (tense sensitive)
  const getText = () => {
    if (!faction || !senator) return null

    if (senatorDetails) {
      return (
        <p>
          <SenatorLink senator={senator} /> became{" "}
          <TermLink name="Rome Consul" displayName="Temporary Rome Consul" />.
        </p>
      )
    } else {
      return (
        <p>
          <SenatorLink senator={senator} /> of the{" "}
          <FactionLink faction={faction} /> now holds the office of{" "}
          <TermLink name="Rome Consul" displayName="Temporary Rome Consul" />,
          making him the <TermLink name="HRAO" />.
        </p>
      )
    }
  }

  if (!faction || !senator) return null

  return (
    <Alert
      icon={getIcon()}
      style={{ backgroundColor: faction.getColor(100) }}
    >
      <b>Temporary Rome Consul</b>
      {getText()}
    </Alert>
  )
}

export default TemporaryRomeConsulNotification
