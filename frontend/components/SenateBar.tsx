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
        <span className="flex shrink-0 flex-col whitespace-nowrap px-4">
          <span className="text-sm text-neutral-600">Presiding magistrate</span>
          {presidingMagistrate ? (
            <span>{presidingMagistrate.displayName}</span>
          ) : (
            <span className="text-neutral-600">None</span>
          )}
        </span>
      </Cell>

      {/* Defeated / vetoed proposals */}
      {game.defeatedProposals.length > 0 && (
        <Cell>
          <Popover
            className={`h-full ${!game.currentProposal ? "border-r border-neutral-300" : ""}`}
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
            <ul className="-mx-4 flex flex-col divide-y divide-neutral-300">
              {game.defeatedProposals.map((proposal, index) => (
                <li key={index} className="px-4 py-2 first:pt-0 last:pb-0">
                  {proposal}
                </li>
              ))}
            </ul>
          </Popover>
        </Cell>
      )}

      {/* Votes + current proposal — only when there is an active proposal */}
      {game.currentProposal && (
        <>
          <Cell>
            <span className="flex w-16 flex-col items-center">
              <span className="text-sm text-neutral-600">Yea</span>
              <span className="tabular-nums">{game.votesYea}</span>
            </span>
          </Cell>
          <Cell>
            <span className="flex w-16 flex-col items-center">
              <span className="text-sm text-neutral-600">Nay</span>
              <span className="tabular-nums">{game.votesNay}</span>
            </span>
          </Cell>
          <Cell>
            <span className="flex flex-col items-center">
              <span className="px-4 text-sm text-neutral-600">Pending</span>
              <span className="tabular-nums">{game.votesPending}</span>
            </span>
          </Cell>
          <div className="flex h-full min-w-0 flex-1 items-center">
            <Popover
              className="h-full w-full min-w-0"
              triggerClassName="h-full min-w-0 w-full flex flex-col justify-center px-4 text-left"
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
          </div>
        </>
      )}
    </div>
  )
}

export default SenateBar
