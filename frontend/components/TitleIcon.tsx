import Image from "next/image"
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import Title from "@/classes/Title"

interface TitleIconProps {
  title: Title
  size: number
  dead?: boolean
  round?: boolean
}

const TitleIcon = ({ title, size, dead, round }: TitleIconProps) => {
  const positionDistance = round ? 6 : 3

  if (title.name.includes("Rome Consul")) {
    return (
      <Image
        className={`absolute z-20 box-border ${dead ? "grayscale-[100%]" : ""}`}
        src={RomeConsulIcon}
        height={size}
        width={size}
        alt="Rome Consul icon"
        style={{ left: positionDistance, bottom: positionDistance }}
      />
    )
  } else {
    return null
  }
}

export default TitleIcon
