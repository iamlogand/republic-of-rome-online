import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import FactionIcon from "@/components/FactionIcon"
import { getXOffset, getYOffset } from "@/functions/trigonometry"
import SenateSeat from "@/components/SenateSeat"
import { useCookieContext } from "@/contexts/CookieContext"

const SECTOR_GAP_ANGLE = 2
const SEAT_GAP = 5

interface SeatData {
  senator: Senator
  angle: number
}

interface SenateSectorProps {
  outerRadius: number
  startAngle: number
  endAngle: number
  senators: Senator[]
  seatSize: number
  faction?: Faction
}

const SenateSector = ({
  outerRadius,
  startAngle,
  endAngle,
  senators,
  seatSize,
  faction,
}: SenateSectorProps) => {
  const { darkMode } = useCookieContext()

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
          backgroundColor:
            (darkMode ? faction?.getColor(700) : faction?.getColor(300)) ??
            (darkMode ? "var(--neutral-600)" : "var(--neutral-200)"),
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
      {innerSeatData.map((seatData, index) => (
        <SenateSeat
          key={index}
          angle={seatData.angle}
          radius={innerRowRadius}
          size={seatSize}
          senator={seatData.senator}
        />
      ))}
      {outerSeatData.map((seatData, index) => (
        <SenateSeat
          key={index}
          angle={seatData.angle}
          radius={outerRowRadius}
          size={seatSize}
          senator={seatData.senator}
        />
      ))}
    </>
  )
}

export default SenateSector
