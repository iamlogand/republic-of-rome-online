import { useEffect, useState } from "react"

import { Alert, Button } from "@mui/material"

import Collection from "@/classes/Collection"
import PotentialAction from "@/classes/PotentialAction"
import styles from "./ProgressSection.module.css"
import Actions from "@/data/actions.json"
import FactionIcon from './FactionIcon'
import { useGameContext } from '@/contexts/GameContext'
import { useAuthContext } from "@/contexts/AuthContext"
import ActionDialog from "@/components/actionDialogs/ActionDialog"
import ActionsType from "@/types/actions"
import Faction from "@/classes/Faction"
import Notification from "@/classes/Notification"
import NotificationContainer from "@/components/notifications/Notification"

const typedActions: ActionsType = Actions;

interface ProgressSectionProps {
  allPotentialActions: Collection<PotentialAction>
  notifications: Collection<Notification>
}

// Progress section showing who players are waiting for
const ProgressSection = (props: ProgressSectionProps) => {
  const { user } = useAuthContext()
  const { allPlayers, allFactions } = useGameContext()
  const [potentialActions, setPotentialActions] = useState<Collection<PotentialAction>>(new Collection<PotentialAction>())
  const [dialogOpen, setDialogOpen] = useState<boolean>(false)
  const [faction, setFaction] = useState<Faction | null>(null)

  useEffect(() => {
    const player = allPlayers.asArray.find(p => p.user?.id === user?.id)
    setFaction(allFactions.asArray.find(f => f.player === player?.id) ?? null)
  }, [user, allPlayers, allFactions, setFaction])
  
  useEffect(() => {
    setPotentialActions(new Collection<PotentialAction>(props.allPotentialActions.asArray.filter(a => a.faction === faction?.id)))
  }, [props.allPotentialActions, faction, setPotentialActions])

  if (potentialActions) {
    const requiredAction = potentialActions.asArray.find(a => a.required === true)

    return (
      <section className={styles.progressSection}>
        <div className={styles.notificationArea}>
          <h3 style={{ lineHeight: '40px' }}>Notifications</h3>
          <div className={styles.notificationList}>
            { props.notifications && props.notifications.asArray.map((notification) =>
              <NotificationContainer notification={notification} />
            )}
          </div>
        </div>
        <div className={styles.actionArea}>
          <h3>Actions</h3>
          <div className={styles.potentialActionArea}>
            {props.allPotentialActions.asArray.map((potentialAction) => {
              const faction = allFactions.byId[potentialAction.faction] ?? null

              return (
                <div className={styles.potentialAction}>
                  <Alert icon={<FactionIcon faction={faction} size={17} selectable />} style={{backgroundColor: 'var(--background-color-alt)'}}>
                    Waiting for {faction?.getName()} Faction to {typedActions[potentialAction.type]["sentence"]}
                  </Alert>
                </div>
              )
            })}
          </div>
          { potentialActions.allIds.length > 0 && requiredAction ?
            <>
              <Button variant="contained" onClick={() => setDialogOpen(true)}>{typedActions[requiredAction.type]["title"]}</Button>
              <ActionDialog potentialActions={potentialActions} open={dialogOpen} setOpen={setDialogOpen} onClose={() => setDialogOpen(false)}/>
            </>
            :
            <>{ faction && <Button variant="contained" disabled>Waiting for others</Button> }</>
          }
        </div>
      </section>
    )
  } else {
    return null
  }
}

export default ProgressSection
