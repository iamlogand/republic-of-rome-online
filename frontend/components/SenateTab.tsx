import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import SenatorPortrait from "@/components/SenatorPortrait"
import FactionIcon from "@/components/FactionIcon"
import { getXOffset, getYOffset } from "@/functions/trigonometry"

interface SeatProps {
  angle: number
  radius: number
  seatSize: number
  senator: Senator
}

const Seat = ({ angle, radius, seatSize, senator }: SeatProps) => {
  const xOffset = getXOffset(angle, radius)
  const yOffset = getYOffset(angle, radius)

  return (
    <div
      className="absolute left-1/2 top-1/2 z-10"
      style={{
        transform: `translate(${xOffset}px, ${yOffset}px)`,
        marginLeft: -seatSize / 2,
        marginTop: -seatSize / 2,
      }}
    >
      <div
        className="h-[80px] w-[80px] rounded-full bg-black"
        style={{ width: seatSize, height: seatSize }}
      >
        <SenatorPortrait
          senator={senator}
          size={seatSize}
          selectable
          round
          nameTooltip
        />
      </div>
    </div>
  )
}

interface SeatData {
  senator: Senator
  angle: number
}

interface SectorProps {
  outerRadius: number
  startAngle: number
  endAngle: number
  faction: Faction | null
  senators: Senator[]
  seatSize: number
}

const Sector = ({
  outerRadius,
  startAngle,
  endAngle,
  faction,
  senators,
  seatSize,
}: SectorProps) => {
  const SECTOR_GAP_ANGLE = 2

  const SEAT_GAP = 5

  const innerRadius = outerRadius - seatSize * 2 - SEAT_GAP * 3

  startAngle += SECTOR_GAP_ANGLE / 2
  endAngle -= SECTOR_GAP_ANGLE / 2
  const meanAngle = (startAngle + endAngle) / 2

  const pathArc = endAngle - startAngle > 180 ? 1 : 0

  const innerRowRadius = outerRadius - seatSize * 1.5 - SEAT_GAP * 2
  const outerRowRadius = outerRadius - seatSize * 0.5 - SEAT_GAP
  const innerRowArcLength =
    innerRowRadius * (endAngle - startAngle) * (Math.PI / 180)

  const centerAngle = (startAngle + endAngle) / 2

  const innerCapacity = Math.floor(innerRowArcLength / (seatSize + SEAT_GAP))

  let innerSeatsCount = Math.min(
    innerCapacity,
    senators.length,
    Math.floor(senators.length / 2 + 1)
  )
  if (innerSeatsCount == 0 && senators.length > 1) {
    innerSeatsCount = 1
  }
  const outerSeatsCount = senators.length - innerSeatsCount

  let senatorIndex = 0
  const innerSeatsArcLength =
    innerSeatsCount * seatSize - seatSize + (innerSeatsCount - 1) * SEAT_GAP
  const innerSeatsArcAngle =
    (innerSeatsArcLength / innerRowRadius) * (180 / Math.PI)
  const innerSeatData: SeatData[] = []
  let currentAngle = centerAngle - innerSeatsArcAngle / 2
  for (let i = 0; i < innerSeatsCount; i++) {
    innerSeatData.push({
      senator: senators[senatorIndex],
      angle: currentAngle,
    })
    currentAngle += innerSeatsArcAngle / (innerSeatsCount - 1)
    senatorIndex++
  }

  const outerSeatsArcLength =
    outerSeatsCount * seatSize - seatSize + (outerSeatsCount - 1) * SEAT_GAP
  const outerSeatsArcAngle =
    (outerSeatsArcLength / outerRowRadius) * (180 / Math.PI)
  const outerSeatData: SeatData[] = []
  currentAngle = centerAngle - outerSeatsArcAngle / 2
  for (let i = 0; i < outerSeatsCount; i++) {
    outerSeatData.push({
      senator: senators[senatorIndex],
      angle: currentAngle,
    })
    currentAngle += outerSeatsArcAngle / (outerSeatsCount - 1)
    senatorIndex++
  }

  return (
    <>
      <div
        className="absolute right-1/2 bottom-1/2 translate-x-1/2 translate-y-1/2 bg-neutral-200"
        style={{
          width: outerRadius * 2,
          height: outerRadius * 2,
          backgroundColor: faction?.getColor(300) ?? "var(--neutral-300)",
          clipPath: `path('\
            M ${outerRadius + getXOffset(startAngle, innerRadius)} ${
            outerRadius + getYOffset(startAngle, innerRadius)
          } \
            L ${outerRadius + getXOffset(startAngle, outerRadius)} ${
            outerRadius + getYOffset(startAngle, outerRadius)
          } \
            A ${outerRadius} ${outerRadius} 0 ${pathArc} 1 ${
            outerRadius + getXOffset(endAngle, outerRadius)
          } ${outerRadius + getYOffset(endAngle, outerRadius)} \
            L ${outerRadius + getXOffset(endAngle, innerRadius)} ${
            outerRadius + getYOffset(endAngle, innerRadius)
          } \
            A ${innerRadius} ${innerRadius} 0 ${pathArc} 0 ${
            outerRadius + getXOffset(startAngle, innerRadius)
          } ${outerRadius + getYOffset(startAngle, innerRadius)} \
            ')`,
        }}
      ></div>
      {faction && (
        <div className="absolute right-1/2 bottom-1/2 translate-x-1/2 translate-y-1/2">
          <div
            style={{
              transform: `translate(${getXOffset(
                meanAngle,
                innerRadius - 25
              )}px, ${getYOffset(meanAngle, innerRadius - 25)}px)`,
            }}
          >
            <FactionIcon faction={faction} size={30} selectable />
          </div>
        </div>
      )}
      {innerSeatData.map((seatData) => (
        <Seat
          angle={seatData.angle}
          radius={innerRowRadius}
          seatSize={seatSize}
          senator={seatData.senator}
        />
      ))}
      {outerSeatData.map((seatData) => (
        <Seat
          angle={seatData.angle}
          radius={outerRowRadius}
          seatSize={seatSize}
          senator={seatData.senator}
        />
      ))}
    </>
  )
}

interface SectorData {
  faction: Faction | null
  senators: Senator[]
  space: number
  startAngle: number
  endAngle: number
}

const SenateTab = () => {
  const EMPTY_SPACE_ANGLE = 50
  const SIZE = 720
  const MARGIN = 10
  const outerRadius = SIZE / 2 - MARGIN

  const { allFactions, allSenators } = useGameContext()

  let sectors: SectorData[] = []
  allFactions.asArray.forEach((faction) => {
    const senators = allSenators.asArray
      .filter((senator) => senator.alive && senator.faction === faction.id)
      .sort((a, b) => a.rank! - b.rank!)
    sectors.push({
      faction: faction,
      senators: senators,
      space: 0,
      startAngle: 0,
      endAngle: 0,
    })
  })

  const unalignedSenators = allSenators.asArray
    .filter((senator) => senator.alive && senator.faction === null)
    .sort((a, b) => a.influence - b.influence)

  sectors.push({
    faction: null,
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
    let actualSpace = Math.max(minimumSpace, representativeSpace)
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
            <Sector
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
