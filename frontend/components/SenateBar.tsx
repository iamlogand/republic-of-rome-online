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

  if (game.phase !== "senate") return null

  return (
    <div className="flex h-16 shrink-0 items-stretch divide-x divide-neutral-300 border-b border-neutral-300">
      {/* Current proposal */}
      <div className="flex flex-1 items-center">
        <span className="flex flex-col px-4">
          <span className="text-sm text-neutral-600">Current proposal</span>
          {game.currentProposal ? (
            <span className="font-bold">{game.currentProposal}</span>
          ) : (
            <span className="text-neutral-600">None</span>
          )}
        </span>
      </div>

      {/* Votes — only when there is an active proposal */}
      {game.currentProposal && (
        <>
          <Cell>
            <span className="flex flex-col items-center px-4">
              <span className="text-sm text-neutral-600">Yea</span>
              <span className="tabular-nums">{game.votesYea}</span>
            </span>
          </Cell>
          <Cell>
            <span className="flex flex-col items-center px-4">
              <span className="text-sm text-neutral-600">Nay</span>
              <span className="tabular-nums">{game.votesNay}</span>
            </span>
          </Cell>
          <Cell>
            <span className="flex flex-col items-center px-4">
              <span className="text-sm text-neutral-600">Pending</span>
              <span className="tabular-nums">{game.votesPending}</span>
            </span>
          </Cell>
        </>
      )}

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
