import { useEffect, useRef, useState } from "react"

import { Alert, Button } from "@mui/material"

import Collection from "@/classes/Collection"
import PotentialAction from "@/classes/PotentialAction"
import styles from "./ProgressSection.module.css"
import Actions from "@/data/actions.json"
import FactionIcon from '@/components/FactionIcon'
import { useGameContext } from '@/contexts/GameContext'
import { useAuthContext } from "@/contexts/AuthContext"
import ActionDialog from "@/components/actionDialogs/ActionDialog"
import ActionsType from "@/types/actions"
import Faction from "@/classes/Faction"
import ActionLog from "@/classes/ActionLog"
import Notification from "@/components/actionLogs/ActionLog"

const typedActions: ActionsType = Actions

interface ProgressSectionProps {
  allPotentialActions: Collection<PotentialAction>
  notifications: Collection<ActionLog>
}

// Progress section showing who players are waiting for
const ProgressSection = (props: ProgressSectionProps) => {
  const { user } = useAuthContext()
  const { allPlayers, allFactions } = useGameContext()
  const [potentialActions, setPotentialActions] = useState<Collection<PotentialAction>>(new Collection<PotentialAction>())
  const [dialogOpen, setDialogOpen] = useState<boolean>(false)
  const [faction, setFaction] = useState<Faction | null>(null)
  const notificationListRef = useRef<HTMLDivElement>(null)
  const [scrollToBottom, setScrollToBottom] = useState(false);

  // Update faction
  useEffect(() => {
    const player = allPlayers.asArray.find(p => p.user?.id === user?.id)
    setFaction(allFactions.asArray.find(f => f.player === player?.id) ?? null)
  }, [user, allPlayers, allFactions, setFaction])
  
  // Update potential actions
  useEffect(() => {
    setPotentialActions(new Collection<PotentialAction>(props.allPotentialActions.asArray.filter(a => a.faction === faction?.id)))
  }, [props.allPotentialActions, faction, setPotentialActions])

  // Scroll to the bottom of the notification list when `scrollToBottom` is true
  useEffect(() => {
    if (scrollToBottom && notificationListRef.current) {
      const scrollableDiv = notificationListRef.current
      scrollableDiv.scrollTo({
        top: scrollableDiv.scrollHeight,
        behavior: 'smooth', // Enable smooth scrolling
      })
      setScrollToBottom(false)
    }
  }, [scrollToBottom])

  // Scroll to the bottom when the notification list is updated
  useEffect(() => {
    setScrollToBottom(true)
  }, [props.notifications.allIds.length])

  if (potentialActions) {
    const requiredAction = potentialActions.asArray.find(a => a.required === true)

    return (
      <div className={styles.progressArea}>
        <div className={styles.notificationArea}>
          <h3 style={{ lineHeight: '40px' }}>Notifications</h3>
          <div ref={notificationListRef} className={styles.notificationList}>
            {props.notifications && props.notifications.asArray.sort((a, b) => a.index - b.index).map((notification) =>
              <Notification key={notification.id} notification={notification} />
            )}
          </div>
        </div>
        <div className={styles.actionArea}>
          <h3>Actions</h3>
          <div className={styles.potentialActionArea}>
            {props.allPotentialActions.asArray.map((potentialAction) => {
              const faction = allFactions.byId[potentialAction.faction] ?? null

              return (
                <Alert key={potentialAction.id}
                  icon={<FactionIcon faction={faction} size={17} selectable />}
                  style={{backgroundColor: 'var(--background-color-neutral)'}}
                >
                  Waiting for {faction?.getName()} Faction to {typedActions[potentialAction.type]["sentence"]}
                </Alert>
              )
            })}
          </div>
          { potentialActions.allIds.length > 0 && requiredAction ?
            <>
              <Button variant="contained" onClick={() => setDialogOpen(true)}>{typedActions[requiredAction.type]["title"]}</Button>
              <ActionDialog potentialActions={potentialActions} open={dialogOpen} setOpen={setDialogOpen} onClose={() => setDialogOpen(false)}/>
            </>
            :
            <>{faction && <Button variant="contained" disabled>Waiting for others</Button>}</>
          }
        </div>
      </div>
    )
  } else {
    return null
  }
}

export default ProgressSection
