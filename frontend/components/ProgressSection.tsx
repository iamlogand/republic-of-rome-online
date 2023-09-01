import { useEffect, useState } from "react"

import { Button } from "@mui/material"

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

const typedActions: ActionsType = Actions;

interface ProgressSectionProps {
  allPotentialActions: Collection<PotentialAction>
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
        <div className={styles.actionItems}>
          {props.allPotentialActions.asArray.map((potentialAction) => {
            const faction = allFactions.byId[potentialAction.faction] ?? null

            return (
              <div key={potentialAction.id}>
                <FactionIcon faction={faction} size={17} selectable />
                <p><i>Waiting for {faction?.getName()} Faction to {typedActions[potentialAction.type]["sentence"]}</i></p>
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
      </section>
    )
  } else {
    return null
  }
}

export default ProgressSection
