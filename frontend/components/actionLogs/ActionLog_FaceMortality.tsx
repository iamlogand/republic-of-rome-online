import Image from 'next/image'
import { Alert } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"
import Faction from "@/classes/Faction"
import DeadIcon from "@/images/icons/dead.svg"
import styles from "./ActionLog.module.css"
import Senator from '@/classes/Senator'
import SenatorLink from "@/components/SenatorLink"
import FactionLink from '@/components/FactionLink'

interface NotificationProps {
  notification: ActionLog
  senatorDetails?: boolean
}

// Notification for when a senator dies during the mortality phase
const FaceMortalityNotification = ({ notification, senatorDetails } : NotificationProps) => {
  const { allFactions, allSenators } = useGameContext()

  // Get notification-specific data
  const faction: Faction | null = notification.faction ? allFactions.byId[notification.faction] ?? null : null
  const senator: Senator | null = notification.data.senator ? allSenators.byId[notification.data.senator] ?? null : null
  const heir: Senator | null = notification.data.senator ? allSenators.byId[notification.data.heir_senator] ?? null : null
  const majorOfficeName: string = notification.data.major_office 
  
  const getIcon = () => (
    <div className={styles.icon}>
      <Image src={DeadIcon} alt="Dead" width={30} height={30} />
    </div>
  )

  // Get the text for the notification (tense sensitive)
  const getText = () => {
    if (!faction || !senator) return null

    return (
      <p>
      {majorOfficeName || heir ? <span>The</span> : null}
      {majorOfficeName && <span> {majorOfficeName}</span>}
      {majorOfficeName && heir ? <span> and</span> : null}
      {heir && <span> <FactionLink faction={faction} /> Leader</span>}
      {majorOfficeName || heir ? <span>, </span> : null}
      <SenatorLink senator={senator} />
      {!heir && <span> of the <FactionLink faction={faction} /></span>}
      <span> {!senatorDetails && "has"} passed away.</span>
      {heir && <span> His heir <SenatorLink senator={heir} /> {!senatorDetails && "has"} replaced him as Faction Leader.</span>}
    </p>
    )
  }

  if (!faction || !senator) return null

  return (
    <Alert icon={getIcon()} style={{backgroundColor: faction.getColor("textBg")}}>
      <b>Mortality</b>
      {getText()}
    </Alert>
  )
}

export default FaceMortalityNotification
