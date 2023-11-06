import Image from "next/image"
import { Alert } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import DeadIcon from "@/images/icons/dead.svg"
import styles from "./ActionLog.module.css"
import Senator from "@/classes/Senator"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "@/components/FactionLink"
import TermLink from "@/components/TermLink"

interface NotificationProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// Notification for when a senator dies during the mortality phase
const FaceMortalityNotification = ({
  notification,
  senatorDetails,
}: NotificationProps) => {
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
    <div className={styles.icon}>
      <Image
        src={DeadIcon}
        alt="Skull and crossbones icon"
        width={30}
        height={30}
      />
    </div>
  )

  // Get the text for the notification (tense sensitive)
  const getText = () => {
    if (!senator) {
      return <p>All senators have survived the Mortality Phase.</p>
    }

    return (
      <p>
        {majorOfficeName || heir ? <span>The</span> : null}
        {majorOfficeName && (
          <span>
            {" "}
            <TermLink
              name={
                majorOfficeName == "Temporary Rome Consul"
                  ? "Rome Consul"
                  : majorOfficeName
              }
              displayName={majorOfficeName}
            />
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
            replaced him as Faction Leader.
          </span>
        )}
      </p>
    )
  }

  return (
    <Alert
      icon={getIcon()}
      style={
        faction
          ? { backgroundColor: faction.getColor(100) }
          : { backgroundColor: "var(--background-color-neutral)" }
      }
    >
      <b>{!senator && "No "}Mortality </b>
      {getText()}
    </Alert>
  )
}

export default FaceMortalityNotification
