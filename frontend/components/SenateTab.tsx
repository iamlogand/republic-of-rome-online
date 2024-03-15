import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import SenateSector from "@/components/SenateSector"

const EMPTY_SPACE_ANGLE = 50 // Angular distance between sectors
const SIZE = 720 // Width of the Senate diagram
const MARGIN = 10 // Margin around the diagram

interface SectorData {
  senators: Senator[]
  space: number
  startAngle: number
  endAngle: number
  faction?: Faction
}

const SenateTab = () => {
  const { allFactions, allSenators } = useGameContext()

  const outerRadius = SIZE / 2 - MARGIN

  let sectors: SectorData[] = []
  allFactions.asArray.forEach((faction) => {
    const senators = allSenators.asArray
      .filter((senator) => senator.alive && senator.faction === faction.id)
      .sort((a, b) => a.rank! - b.rank!)
    sectors.push({
      senators: senators,
      space: 0,
      startAngle: 0,
      endAngle: 0,
      faction: faction,
    })
  })

  const unalignedSenators = allSenators.asArray
    .filter((senator) => senator.alive && senator.faction === null)
    .sort((a, b) => a.influence - b.influence)

  sectors.push({
    senators: unalignedSenators,
    space: 0,
    startAngle: 0,
    endAngle: 0,
  })

  sectors = sectors.sort((a, b) => a.senators.length - b.senators.length)
  sectors = sectors.filter((sector) => sector.senators.length > 0)

  const totalMembers = sectors.reduce(
    (acc, sector) => acc + sector.senators.length,
    0
  )
  const seatSize = Math.max(40, Math.min(80, 110 - totalMembers * 1.5))

  const minimumSpace = (0.055 * seatSize) / 80

  let remainingSpace = 1
  let remainingMembers = totalMembers
  sectors.forEach((sector) => {
    const representativeSpace =
      (sector.senators.length * remainingSpace) / remainingMembers
    const actualSpace = Math.max(minimumSpace, representativeSpace)
    sector.space = actualSpace
    remainingSpace -= actualSpace
    remainingMembers -= sector.senators.length
  })

  sectors.sort((a, b) =>
    a.faction && b.faction
      ? a.faction.rank - b.faction.rank
      : a.faction
      ? -1
      : 1
  )

  let currentAngle = EMPTY_SPACE_ANGLE / 2
  const totalAngle = 360 - EMPTY_SPACE_ANGLE
  sectors.forEach((sector) => {
    sector.startAngle = currentAngle
    sector.endAngle = currentAngle + totalAngle * sector.space
    currentAngle += totalAngle * sector.space
  })

  return (
    <div className="h-full w-full overflow-auto box-border">
      <div
        className="h-full w-full flex justify-center items-center"
        style={{ minWidth: SIZE, minHeight: SIZE - 35 }}
      >
        <div className="relative mt-[-35px]">
          {sectors.map((sector) => (
            <SenateSector
              key={sector.faction?.id ?? -1}
              outerRadius={outerRadius}
              startAngle={sector.startAngle}
              endAngle={sector.endAngle}
              faction={sector.faction}
              senators={sector.senators}
              seatSize={seatSize}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default SenateTab
