"use client"

import { useCallback, useEffect, useMemo, useRef } from "react"

import Senator from "@/classes/Senator"
import useCustomActionForm from "@/hooks/useCustomActionForm"

import { CustomActionFormProps } from "../ActionBar"
import { ActionSelection } from "../GenericActionForm"

type Decision = "yea" | "nay" | "abstain"

interface SenatorVoteEntry {
  decision: Decision | null
  boughtVotes: number
}

type SenatorVoteState = Record<number, SenatorVoteEntry>

const AdvancedVoteForm = ({
  availableAction,
  publicGameState,
  selection,
  setSelection,
  isExpanded,
  setIsExpanded,
  onSubmitSuccess,
}: CustomActionFormProps) => {
  const {
    dialogRef,
    feedback,
    loading,
    openDialog,
    closeDialog,
    handleDialogClose,
    submit,
  } = useCustomActionForm({
    availableAction,
    publicGameState,
    isExpanded,
    setIsExpanded,
    onSubmitSuccess,
  })

  const setSelectionRef = useRef(setSelection)
  useEffect(() => {
    setSelectionRef.current = setSelection
  })

  const factionId = availableAction.faction

  const ownSenators: Senator[] = useMemo(
    () =>
      publicGameState.senators
        .filter((s) => s.faction === factionId && s.alive)
        .sort((a, b) => a.displayName.localeCompare(b.displayName)),
    [publicGameState.senators, factionId],
  )

  // §1.09.14: abstaining is not allowed during the passage or repeal of a land
  // bill, so senators start undecided and must each be given a yea or a nay
  const currentProposal = publicGameState.game?.currentProposal ?? ""
  const isLandBillVote =
    currentProposal.startsWith("Pass type ") ||
    currentProposal.startsWith("Repeal type ")
  const defaultDecision: Decision | null = isLandBillVote ? null : "abstain"

  // §1.09.821: the Consul for Life nominee adds his influence to his vote total
  const isConsulForLifeVote = currentProposal.startsWith(
    "Elect Consul for Life ",
  )
  const votesFor = (senator: Senator) =>
    senator.votes +
    (isConsulForLifeVote && senator.statusItems.includes("named in proposal")
      ? senator.influence
      : 0)

  const voteState = (selection["VoteState"] ??
    {}) as unknown as SenatorVoteState

  const decisionFor = (senatorId: number): Decision | null =>
    voteState[senatorId]?.decision ?? defaultDecision

  const setVoteState = (
    updater: SenatorVoteState | ((prev: SenatorVoteState) => SenatorVoteState),
  ) => {
    setSelection((prev) => {
      const current = ((prev ?? {})["VoteState"] ??
        {}) as unknown as SenatorVoteState
      const next = typeof updater === "function" ? updater(current) : updater
      return { ...(prev ?? {}), VoteState: next } as unknown as ActionSelection
    })
  }

  const initializeState = useCallback(() => {
    setSelectionRef.current((prev) => {
      const existing = ((prev ?? {})["VoteState"] ??
        {}) as unknown as SenatorVoteState
      const initial: SenatorVoteState = {}
      ownSenators.forEach((s) => {
        initial[s.id] = existing[s.id] ?? {
          decision: defaultDecision,
          boughtVotes: 0,
        }
      })
      return {
        ...(prev ?? {}),
        VoteState: initial,
      } as unknown as ActionSelection
    })
  }, [ownSenators, defaultDecision])

  const handleOpenDialog = () => {
    initializeState()
    openDialog()
  }

  useEffect(() => {
    if (isExpanded) {
      initializeState()
    }
  }, [isExpanded, initializeState])

  const setDecision = (senatorId: number, decision: Decision) => {
    setVoteState((prev) => ({
      ...prev,
      [senatorId]: {
        ...prev[senatorId],
        decision,
        boughtVotes:
          decision === "abstain" ? 0 : (prev[senatorId]?.boughtVotes ?? 0),
      },
    }))
  }

  const setBoughtVotes = (senatorId: number, newValue: number) => {
    setVoteState((prev) => ({
      ...prev,
      [senatorId]: { ...prev[senatorId], boughtVotes: newValue },
    }))
  }

  const handleAllYea = () => {
    setVoteState((prev) => {
      const next = { ...prev }
      ownSenators.forEach((s) => {
        next[s.id] = { ...next[s.id], decision: "yea" }
      })
      return next
    })
  }

  const handleAllNay = () => {
    setVoteState((prev) => {
      const next = { ...prev }
      ownSenators.forEach((s) => {
        next[s.id] = { ...next[s.id], decision: "nay" }
      })
      return next
    })
  }

  const handleClear = () => {
    setVoteState((prev) => {
      const next = { ...prev }
      ownSenators.forEach((s) => {
        next[s.id] = { decision: defaultDecision, boughtVotes: 0 }
      })
      return next
    })
  }

  const totalCost = ownSenators.reduce(
    (sum, senator) => sum + (voteState[senator.id]?.boughtVotes ?? 0),
    0,
  )

  const { projectedYea, projectedNay } = ownSenators.reduce(
    (projections, senator) => {
      const entry = voteState[senator.id]
      if (!entry) return projections
      const effectiveVotes = votesFor(senator) + entry.boughtVotes
      if (entry.decision === "yea") projections.projectedYea += effectiveVotes
      if (entry.decision === "nay") projections.projectedNay += effectiveVotes
      return projections
    },
    { projectedYea: 0, projectedNay: 0 },
  )

  const undecided = ownSenators.some((s) => decisionFor(s.id) === null)

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (undecided) return
    await submit({
      senator_votes: Object.fromEntries(
        ownSenators.map((s) => [
          String(s.id),
          {
            decision: decisionFor(s.id) ?? "abstain",
            bought_votes: voteState[s.id]?.boughtVotes ?? 0,
          },
        ]),
      ),
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <button
        type="button"
        onClick={handleOpenDialog}
        className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
      >
        Advanced vote...
      </button>

      <dialog
        ref={dialogRef}
        onClose={handleDialogClose}
        className="min-w-[24rem] rounded-lg bg-white p-6 shadow-lg"
      >
        <div className="flex flex-col gap-6">
          <div className="flex w-0 min-w-full flex-col gap-4">
            <h3 className="text-xl">Advanced vote</h3>
            {isLandBillVote && (
              <p className="text-sm text-neutral-600">
                Abstaining is not allowed during a land bill vote, so every
                senator must vote yea or nay.
              </p>
            )}
          </div>
          {feedback && (
            <div className="inline-flex max-w-[600px] rounded-md bg-red-50 px-2 py-1 text-red-600">
              <p>{feedback}</p>
            </div>
          )}

          <div className="flex items-center justify-between gap-10">
            <div className="flex gap-4">
              <span className="inline-block w-14">Yea: {projectedYea}</span>
              <span className="inline-block w-14">Nay: {projectedNay}</span>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleAllYea}
                disabled={ownSenators.every((s) => decisionFor(s.id) === "yea")}
                className="select-none rounded-md border border-neutral-600 px-3 py-1 text-sm text-neutral-600 hover:bg-neutral-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
              >
                All yea
              </button>
              <button
                type="button"
                onClick={handleAllNay}
                disabled={ownSenators.every((s) => decisionFor(s.id) === "nay")}
                className="select-none rounded-md border border-neutral-600 px-3 py-1 text-sm text-neutral-600 hover:bg-neutral-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
              >
                All nay
              </button>
              <button
                type="button"
                onClick={handleClear}
                disabled={ownSenators.every(
                  (s) =>
                    decisionFor(s.id) === defaultDecision &&
                    voteState[s.id]?.boughtVotes === 0,
                )}
                className="select-none rounded-md border border-neutral-600 px-3 py-1 text-sm text-neutral-600 hover:bg-neutral-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="flex flex-col gap-4">
            {ownSenators.map((senator) => {
              const entry = voteState[senator.id]
              const decision = decisionFor(senator.id)
              const boughtVotes = entry?.boughtVotes ?? 0
              const votesLocked = decision !== "yea" && decision !== "nay"
              return (
                <div key={senator.id} className="flex flex-col">
                  <span>{senator.displayName}</span>
                  <div className="flex justify-between gap-6">
                    <div className="flex flex-col gap-1">
                      <span className="text-sm text-neutral-600">
                        {votesFor(senator)}{" "}
                        {votesFor(senator) === 1 ? "vote" : "votes"}
                      </span>
                      <div className="flex gap-1">
                        <button
                          type="button"
                          onClick={() => setDecision(senator.id, "yea")}
                          className={
                            decision === "yea"
                              ? "cursor-default select-none rounded-md border border-green-600 bg-green-100 px-3 py-1 text-green-800"
                              : "select-none rounded-md border border-neutral-400 px-3 py-1 text-neutral-600 hover:bg-neutral-100"
                          }
                        >
                          Yea
                        </button>
                        <button
                          type="button"
                          onClick={() => setDecision(senator.id, "nay")}
                          className={
                            decision === "nay"
                              ? "cursor-default select-none rounded-md border border-red-600 bg-red-100 px-3 py-1 text-red-800"
                              : "select-none rounded-md border border-neutral-400 px-3 py-1 text-neutral-600 hover:bg-neutral-100"
                          }
                        >
                          Nay
                        </button>
                        {!isLandBillVote && (
                          <button
                            type="button"
                            onClick={() => setDecision(senator.id, "abstain")}
                            className={
                              decision === "abstain"
                                ? "cursor-default select-none rounded-md border border-blue-600 bg-blue-100 px-3 py-1 text-blue-800"
                                : "select-none rounded-md border border-neutral-400 px-3 py-1 text-neutral-600 hover:bg-neutral-100"
                            }
                          >
                            Abstain
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col gap-1 text-sm text-neutral-600">
                      <div className="flex justify-between">
                        <span className={votesLocked ? "text-neutral-400" : ""}>
                          Buy votes
                        </span>
                        <button
                          type="button"
                          onClick={() =>
                            setBoughtVotes(senator.id, senator.talents)
                          }
                          disabled={
                            votesLocked || boughtVotes >= senator.talents
                          }
                          className="cursor-pointer text-blue-600 underline-offset-2 hover:underline disabled:cursor-default disabled:text-neutral-400 disabled:no-underline"
                        >
                          Max {senator.talents}T
                        </button>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() =>
                            setBoughtVotes(senator.id, boughtVotes - 1)
                          }
                          disabled={boughtVotes <= 0 || votesLocked}
                          className="relative h-6 min-w-6 rounded-full border border-red-600 text-red-600 hover:bg-red-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                        >
                          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                            &minus;
                          </div>
                        </button>
                        <input
                          type="number"
                          min={0}
                          max={senator.talents}
                          value={boughtVotes}
                          disabled={votesLocked}
                          onChange={(e) => {
                            const newVal = Math.max(
                              0,
                              Math.min(senator.talents, Number(e.target.value)),
                            )
                            setBoughtVotes(senator.id, newVal)
                          }}
                          className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5 disabled:border-neutral-300 disabled:text-neutral-400"
                        />
                        <button
                          type="button"
                          onClick={() =>
                            setBoughtVotes(senator.id, boughtVotes + 1)
                          }
                          disabled={
                            boughtVotes >= senator.talents || votesLocked
                          }
                          className="relative h-6 min-w-6 rounded-full border border-green-600 text-green-600 hover:bg-green-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                        >
                          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                            +
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="text-sm">
            {totalCost === 0 ? (
              <span className="text-neutral-600">No talents spent</span>
            ) : (
              <span>
                Senators will spend{" "}
                <span className="font-semibold">{totalCost}T</span> to buy votes
              </span>
            )}
          </div>

          <div className="mt-4 flex justify-end gap-4">
            <button
              type="button"
              onClick={closeDialog}
              className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="select-none rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
              disabled={loading || undecided}
            >
              Confirm
            </button>
          </div>
        </div>
      </dialog>
    </form>
  )
}

export default AdvancedVoteForm
