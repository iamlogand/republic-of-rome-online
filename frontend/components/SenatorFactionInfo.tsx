import Faction from "@/classes/Faction"
import { useGameContext } from "@/contexts/GameContext"
import FactionLink from "@/components/FactionLink"
import Senator from "@/classes/Senator"
import FactionIcon from "@/components/FactionIcon"
import FactionName from "@/components/FactionName"
import TermLink from "@/components/TermLink"

interface SenatorFactionInfoProps {
  senator: Senator
  selectable?: boolean
}

const SenatorFactionInfo = ({
  senator,
  selectable,
}: SenatorFactionInfoProps) => {
  const { allFactions, allTitles } = useGameContext()

  // Get senator-specific data
  const faction: Faction | null = senator?.faction
    ? allFactions.byId[senator.faction] ?? null
    : null
  const isFactionLeader: boolean = senator
    ? allTitles.asArray.some(
        (t) => t.senator === senator.id && t.name == "Faction Leader"
      )
    : false

  // Get JSX for the faction description
  const getFactionDescription = () => {
    if (!faction) return null
    return (
      <span>
        {selectable ? (
          <FactionLink faction={faction} includeIcon={true} />
        ) : (
          <span>
            <span style={{ marginRight: 4 }}>
              <FactionIcon faction={faction} size={17} />
            </span>
            <FactionName faction={faction} />
          </span>
        )}
        {isFactionLeader ? " Leader" : " Member"}
      </span>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <p>
        {faction && senator.alive ? (
          <span>{getFactionDescription()}</span>
        ) : senator.alive ? (
          <TermLink name="Unaligned" hiddenUnderline />
        ) : (
          <span>
            {faction ? (
              <span>Died as {getFactionDescription()}</span>
            ) : (
              <span>
                Was always <TermLink name="Unaligned" hiddenUnderline />
              </span>
            )}
          </span>
        )}
      </p>
    </div>
  )
}

export default SenatorFactionInfo
