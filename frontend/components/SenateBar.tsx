import PublicGameState from "@/classes/PublicGameState"
import Popover from "@/components/Popover"

interface Props {
  publicGameState: PublicGameState
}

const Cell = ({ children }: { children: React.ReactNode }) => (
  <div className="flex h-full items-center">{children}</div>
)

const SenateBar = ({ publicGameState }: Props) => {
  const game = publicGameState.game!

  const presidingMagistrate = publicGameState.senators.find((s) =>
    s.titles.includes("presiding magistrate"),
  )

  if (game.phase !== "senate") return null

  return (
    <div className="flex h-16 shrink-0 items-stretch divide-x divide-neutral-300 border-b border-neutral-300">
      {/* Presiding magistrate */}
      <Cell>
        <span className="flex flex-col px-4">
          <span className="text-sm text-neutral-600">Presiding magistrate</span>
          {presidingMagistrate ? (
            <span>{presidingMagistrate.displayName}</span>
          ) : (
            <span className="text-neutral-600">None</span>
          )}
        </span>
      </Cell>

      {/* Votes */}
      <>
        <Cell>
          <span className="flex w-16 flex-col items-center">
            <span className="text-sm text-neutral-600">Yea</span>
            <span className="tabular-nums">
              {game.currentProposal ? game.votesYea : "-"}
            </span>
          </span>
        </Cell>
        <Cell>
          <span className="flex w-16 flex-col items-center">
            <span className="text-sm text-neutral-600">Nay</span>
            <span className="tabular-nums">
              {game.currentProposal ? game.votesNay : "-"}
            </span>
          </span>
        </Cell>
        <Cell>
          <span className="flex flex-col items-center">
            <span className="px-4 text-sm text-neutral-600">Pending</span>
            <span className="tabular-nums">
              {game.currentProposal ? game.votesPending : "-"}
            </span>
          </span>
        </Cell>
      </>

      {/* Current proposal */}
      <div className="flex min-w-0 flex-1 items-center">
        {game.currentProposal ? (
          <Popover
            className="h-full min-w-0 flex-1"
            triggerClassName="h-full flex flex-col justify-center px-4 min-w-0"
            trigger={
              <>
                <span className="text-sm text-neutral-600">
                  Current proposal
                </span>
                <span className="truncate font-bold">
                  {game.currentProposal}
                </span>
              </>
            }
          >
            <div className="max-w-lg">{game.currentProposal}</div>
          </Popover>
        ) : (
          <span className="flex flex-col px-4">
            <span className="text-sm text-neutral-600">Current proposal</span>
            <span className="text-neutral-600">-</span>
          </span>
        )}
      </div>

      {/* Defeated / vetoed proposals */}
      {game.defeatedProposals.length > 0 && (
        <Cell>
          <Popover
            className="h-full"
            triggerClassName="h-full flex flex-col items-center justify-center px-4"
            trigger={
              <>
                <span className="text-sm text-neutral-600">Defeated</span>
                <span className="tabular-nums">
                  {game.defeatedProposals.length}
                </span>
              </>
            }
          >
            <ul className="flex flex-col gap-1">
              {game.defeatedProposals.map((proposal, index) => (
                <li key={index}>{proposal}</li>
              ))}
            </ul>
          </Popover>
        </Cell>
      )}
    </div>
  )
}

export default SenateBar
