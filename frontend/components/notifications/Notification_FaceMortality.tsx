import Image from 'next/image'
import { Alert } from "@mui/material"

import Notification from "@/classes/Notification"
import { useGameContext } from "@/contexts/GameContext"
import { useEffect, useState } from "react"
import Faction from "@/classes/Faction"
import DeadIcon from "@/images/icons/dead.svg"
import styles from "./Notification.module.css"
import Senator from '@/classes/Senator'
import SenatorLink from "@/components/SenatorLink"
import FactionLink from '@/components/FactionLink'

interface FaceMortalityNotificationProps {
  notification: Notification
}

const FaceMortalityNotification = (props: FaceMortalityNotificationProps) => {
  const { allFactions, allSenators } = useGameContext()
  
  const [faction, setFaction] = useState<Faction | null>(null)
  const [senator, setSenator] = useState<Senator | null>(null)
  const [heir, setHeir] = useState<Senator | null>(null)

  // Update faction
  useEffect(() => {
    if (props.notification.faction) setFaction(allFactions.byId[props.notification.faction] ?? null)
  }, [props.notification, allFactions, setFaction])

  // Update senator and heir
  useEffect(() => {
    if (props.notification.data) {
      setSenator(allSenators.byId[props.notification.data.senator] ?? null)
      setHeir(allSenators.byId[props.notification.data.heir] ?? null)
    }
  }, [props.notification, allSenators, setFaction, setHeir])

  const getIcon = () => (
    <div className={styles.icon}>
      <Image src={DeadIcon} alt="Dead" width={30} height={30} />
    </div>
  )

  if (faction) {
    const majorOffice: string = props.notification.data.major_office  // This is just the name of the office

    if (senator) {
      return (
        <Alert icon={getIcon()} style={{backgroundColor: faction.getColor("textBg")}}>
          <b>Mortality</b>
          <p>
            <>
              {majorOffice || heir ? <span>The</span> : null}
              {majorOffice && <span> {majorOffice} and</span>}
              {heir && <span> <FactionLink faction={faction} /> Leader</span>}
              {majorOffice || heir ? <span>, </span> : null}
              <span><SenatorLink senator={senator} /> has passed away.</span>
              {heir && <span> His heir <SenatorLink senator={heir} /> has replaced him as Faction Leader.</span>}
            </>
          </p>
        </Alert>
      )
    }
  }
  return null
}

export default FaceMortalityNotification
