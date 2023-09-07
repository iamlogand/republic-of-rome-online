import { Alert } from "@mui/material"
import Notification from "@/classes/Notification"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import { useEffect, useState } from "react"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"

interface SelectFactionLeaderNotificationProps {
  notification: Notification
}

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
      return <FactionIcon faction={faction} size={17} selectable />
    } else {
      return false
    }
  }

  if (faction && newFactionLeader) {
    return (
      <Alert icon={getIcon()} style={{backgroundColor: faction.getColor("textBg")}}>
        <b>New Faction Leader</b>
        <p>
          {newFactionLeader.name} now holds the position of {faction?.getName()} Faction Leader
          {oldFactionLeader ? `, taking over from ${oldFactionLeader.name}.` : '.'}
        </p>
      </Alert>
    )
    } else {
    return null
  }
}

export default SelectFactionLeaderNotification