import { useEffect, useState } from "react"
import { Button } from "@mui/material"

import Collection from "@/classes/Collection"
import Action from "@/classes/Action"
import ActionDataCollection from "@/data/actions.json"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import { useCookieContext } from "@/contexts/CookieContext"
import Dialog from "@/components/Dialog"
import ActionDataCollectionType from "@/types/Action"
import Faction from "@/classes/Faction"
import FactionLink from "@/components/FactionLink"

const typedActionDataCollection: ActionDataCollectionType = ActionDataCollection

const ActionsArea = () => {
  const { user } = useCookieContext()
  const {
    turns,
    phases,
    allPlayers,
    allFactions,
    latestActions,
    dialog,
    setDialog,
  } = useGameContext()
  const [thisFactionsPendingActions, setThisFactionsPendingActions] = useState<
    Collection<Action>
  >(new Collection<Action>())
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

  // Get the latest phase
  const latestTurn = turns.asArray.sort((a, b) => a.index - b.index)[
    turns.allIds.length - 1
  ]
  const latestPhases = latestTurn
    ? phases.asArray.filter((p) => p.turn === latestTurn.id)
    : []
  const latestPhase =
    latestPhases.length > 0
      ? latestPhases.sort((a, b) => a.index - b.index)[latestPhases.length - 1]
      : null

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
      <div className="flex flex-col gap-2">
        <h3 className="leading-none m-0 ml-2 text-base text-neutral-600 dark:text-neutral-100">
          Actions
        </h3>
        <div className="p-2 h-[80px] bg-white dark:bg-neutral-600 border border-solid border-neutral-200 dark:border-neutral-750 rounded shadow-inner flex flex-col justify-center gap-3 items-center">
          <p className="text-center">{waitingForDesc}</p>
          <div className="flex gap-3 justify-center">
            {rankedFactions.map((faction, index) => {
              const potential = latestActions.asArray.some(
                (a) => a.faction === faction.id && a.completed === false
              )
              return (
                <div
                  key={index}
                  className="mt-1 flex items-start justify-center gap-3"
                >
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
          {thisFactionsPendingActions.allIds.length > 0 && requiredAction ? (
            <div className="flex flex-col">
              <Button variant="contained" onClick={() => setDialog("action")}>
                {typedActionDataCollection[requiredAction.type]["title"]}
              </Button>
              <Dialog
                actions={thisFactionsPendingActions}
                open={dialog == "action"}
                setOpen={() => setDialog("action")}
                onClose={() => setDialog(null)}
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
    )
  } else {
    return null
  }
}

export default ActionsArea
