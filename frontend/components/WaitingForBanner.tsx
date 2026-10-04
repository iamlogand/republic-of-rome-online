import PublicGameState from "@/classes/PublicGameState"
import { formatList } from "@/helpers/text"

interface Props {
  publicGameState: PublicGameState
}

const WaitingForBanner = ({ publicGameState }: Props) => {
  const groups = publicGameState.pendingDecisions.reduce<
    Record<string, string[]>
  >((acc, pd) => {
    const name =
      publicGameState.factions.find((f) => f.id === pd.factionId)
        ?.displayName ?? "Unknown"
    return { ...acc, [pd.description]: [...(acc[pd.description] ?? []), name] }
  }, {})

  if (Object.keys(groups).length === 0) return null

  return (
    <div className="flex shrink-0 items-center gap-4 border-t border-neutral-300 px-4 py-2">
      {Object.entries(groups).map(([description, factionNames]) => (
        <span key={description}>
          <span className="text-neutral-600">Waiting for </span>
          <span className="font-medium">{formatList(factionNames)}</span>
          <span className="text-neutral-600"> to </span>
          {description}
        </span>
      ))}
    </div>
  )
}

export default WaitingForBanner
