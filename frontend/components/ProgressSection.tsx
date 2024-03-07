import { useEffect, useState } from "react"
import { Button } from "@mui/material"
import EastIcon from "@mui/icons-material/East"

import Collection from "@/classes/Collection"
import Action from "@/classes/Action"
import ActionDataCollection from "@/data/actions.json"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import { useCookieContext } from "@/contexts/CookieContext"
import ActionDialog from "@/components/ActionDialog"
import ActionDataCollectionType from "@/types/Action"
import Faction from "@/classes/Faction"
import FactionLink from "@/components/FactionLink"
import NotificationList from "@/components/NotificationList"

const typedActionDataCollection: ActionDataCollectionType = ActionDataCollection

const SEQUENTIAL_PHASES = ["Forum", "Last Forum"]

interface ProgressSectionProps {
  latestActions: Collection<Action>
}

// Progress section showing who players are waiting for
const ProgressSection = ({ latestActions }: ProgressSectionProps) => {
  const { user } = useCookieContext()
  const { game, latestPhase, allPlayers, allFactions } = useGameContext()
  const [thisFactionsPendingActions, setThisFactionsPendingActions] = useState<
    Collection<Action>
  >(new Collection<Action>())
  const [dialogOpen, setDialogOpen] = useState<boolean>(false)
  const [faction, setFaction] = useState<Faction | null>(null)

  // Update faction
  useEffect(() => {
    const player = allPlayers.asArray.find((p) => p.user?.id === user?.id)
    setFaction(allFactions.asArray.find((f) => f.player === player?.id) ?? null)
  }, [user, allPlayers, allFactions, setFaction])

  // Update actions
  useEffect(() => {
    setThisFactionsPendingActions(
      new Collection<Action>(
        latestActions?.asArray.filter(
          (a) => a.faction === faction?.id && a.completed === false
        ) ?? []
      )
    )
  }, [latestActions, faction, setThisFactionsPendingActions])

  const rankedFactions = allFactions.asArray.sort(
    (a: Faction, b: Faction) => a.rank - b.rank
  )

  if (thisFactionsPendingActions) {
    const requiredAction = thisFactionsPendingActions.asArray.find(
      (a) => a.required === true
    )

    let waitingForDesc = <span></span>
    const pendingActions = latestActions.asArray.filter(
      (a) => a.completed === false
    )
    const firstPotentialAction = pendingActions[0]
    if (pendingActions.length > 1) {
      waitingForDesc = (
        <span>
          Waiting for {pendingActions.length} factions to{" "}
          {typedActionDataCollection[firstPotentialAction.type]["sentence"]}
        </span>
      )
    } else if (pendingActions.length === 1) {
      const onlyPendingFaction = allFactions.asArray.find(
        (f) => f.id === firstPotentialAction.faction
      )
      if (onlyPendingFaction)
        waitingForDesc = (
          <span>
            Waiting for{" "}
            {faction === onlyPendingFaction ? (
              <span>you</span>
            ) : (
              <FactionLink faction={onlyPendingFaction} />
            )}{" "}
            to{" "}
            {typedActionDataCollection[firstPotentialAction.type]["sentence"]}
          </span>
        )
    }

    return (
      <div className="box-border h-full px-4 pt-2 pb-4 flex flex-col gap-4">
        <NotificationList />
        {!game?.end_date && (
          <div className="flex flex-col gap-2">
            <h3 className="leading-none m-0 ml-2 text-base text-neutral-600 dark:text-neutral-100">
              Actions
            </h3>
            <div className="p-2 bg-white dark:bg-neutral-600 border border-solid border-neutral-200 dark:border-neutral-750 rounded shadow-inner flex flex-col gap-3 items-center">
              <p className="text-center">{waitingForDesc}</p>
              <div className="h-full flex gap-3 justify-center">
                {rankedFactions.map((faction, index) => {
                  const potential = latestActions.asArray.some(
                    (a) => a.faction === faction.id && a.completed === false
                  )
                  return (
                    <div
                      key={index}
                      className="mt-1 flex items-start justify-center gap-3"
                    >
                      {index !== 0 &&
                        SEQUENTIAL_PHASES.some(
                          (name) => name === latestPhase?.name
                        ) && (
                          <div className="self-start w-1 h-6 relative">
                            <div className="absolute bottom-1/2 right-1/2 translate-x-1/2 translate-y-1/2">
                              <EastIcon fontSize="small" />
                            </div>
                          </div>
                        )}
                      <div className="w-6 h-6 flex items-start justify-center">
                        <FactionIcon
                          faction={faction}
                          size={!potential ? 18 : 24}
                          muted={!potential}
                          selectable
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
            <div className="my-0">
              {thisFactionsPendingActions.allIds.length > 0 &&
              requiredAction ? (
                <div className="flex flex-col">
                  <Button
                    variant="contained"
                    onClick={() => setDialogOpen(true)}
                  >
                    {typedActionDataCollection[requiredAction.type]["title"]}
                  </Button>
                  <ActionDialog
                    actions={thisFactionsPendingActions}
                    open={dialogOpen}
                    setOpen={setDialogOpen}
                    onClose={() => setDialogOpen(false)}
                  />
                </div>
              ) : (
                <div className="flex flex-col">
                  {faction && (
                    <Button variant="contained" disabled>
                      Waiting for others
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    )
  } else {
    return null
  }
}

export default ProgressSection
