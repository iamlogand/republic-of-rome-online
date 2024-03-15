import Senator from "@/classes/Senator"
import SenatorPortrait from "@/components/SenatorPortrait"
import { getXOffset, getYOffset } from "@/functions/trigonometry"

interface SenateSeatProps {
  angle: number
  radius: number
  size: number
  senator: Senator
}

const SenateSeat = ({ angle, radius, size, senator }: SenateSeatProps) => {
  const xOffset = getXOffset(angle, radius)
  const yOffset = getYOffset(angle, radius)

  return (
    <div
      className="absolute left-1/2 top-1/2 z-10"
      style={{
        transform: `translate(${xOffset}px, ${yOffset}px)`,
        marginLeft: -size / 2,
        marginTop: -size / 2,
      }}
    >
      <div
        className="h-[80px] w-[80px] rounded-full bg-black"
        style={{ width: size, height: size }}
      >
        <SenatorPortrait
          senator={senator}
          size={size}
          selectable
          round
          summary
        />
      </div>
    </div>
  )
}

export default SenateSeat
