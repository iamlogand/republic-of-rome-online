import { Alert } from "@mui/material"
import Notification from "@/classes/Notification"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import { useEffect, useState } from "react"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import styles from "./Notification.module.css"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from '@/components/FactionLink'

interface SelectFactionLeaderNotificationProps {
  notification: Notification
}

// Notification for when a new faction leader is selected
const SelectFactionLeaderNotification = (props: SelectFactionLeaderNotificationProps) => {
  const { allFactions, allSenators } = useGameContext()

  const [faction, setFaction] = useState<Faction | null>(null)
  const [oldFactionLeader, setOldFactionLeader] = useState<Senator | null>(null)
  const [newFactionLeader, setNewFactionLeader] = useState<Senator | null>(null)

  // Update faction
  useEffect(() => {
    if (props.notification.faction) setFaction(allFactions.byId[props.notification.faction] ?? null)
  }, [props.notification, allFactions, setFaction])

  // Update old and new faction leaders
  useEffect(() => {
    if (props.notification.data) {
      setOldFactionLeader(allSenators.byId[props.notification.data.previous_senator] ?? null)
      setNewFactionLeader(allSenators.byId[props.notification.data.senator] ?? null)
    }
  }, [props.notification, allSenators, setOldFactionLeader, setNewFactionLeader])

  const getIcon = () => {
    if (faction) {
      return (
        <div className={styles.icon}>
          <FactionIcon faction={faction} size={18} selectable />
        </div>
      )
    } else {
      return false
    }
  }

  if (faction && newFactionLeader) {
    return (
      <Alert icon={getIcon()} style={{backgroundColor: faction.getColor("textBg")}}>
        <b>New Faction Leader</b>
        <p>
          <SenatorLink senator={newFactionLeader} /> now holds the position of <FactionLink faction={faction} /> Leader
          {oldFactionLeader ? ', taking over from ' + <SenatorLink senator={oldFactionLeader} /> + '.' : '.'}
        </p>
      </Alert>
    )
    } else {
    return null
  }
}

export default SelectFactionLeaderNotification
