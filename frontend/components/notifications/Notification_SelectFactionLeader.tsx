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

  if (faction && oldFactionLeader && newFactionLeader) {
    return (
      <Alert icon={getIcon()} style={{backgroundColor: faction.getColor("textBg")}}>{faction?.getName()} Faction changed their faction leader from {oldFactionLeader.name} to {newFactionLeader.name}</Alert>
    )
    } else {
    return null
  }
}

export default SelectFactionLeaderNotification