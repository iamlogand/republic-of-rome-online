import Image from "next/image"
import MilitaryIcon from "@/images/icons/military.svg"
import War from "@/classes/War"
import Punic1 from "@/images/wars/punic1.png"
import Punic2 from "@/images/wars/punic2.png"
import Gallic1 from "@/images/wars/gallic1.png"
import Macedonian1 from "@/images/wars/macedonian1.png"
import Macedonian2 from "@/images/wars/macedonian2.png"
import Illyrain1 from "@/images/wars/illyrian1.png"
import Illyrain2 from "@/images/wars/illyrian2.png"
import Syrian from "@/images/wars/syrian1.png"

interface WarPortraitProps {
  war: War
}

const WarPortrait = ({ war }: WarPortraitProps) => {
  const getImage = () => {
    if (war.getName() === "1st Punic War") return Punic1
    if (war.getName() === "2nd Punic War") return Punic2
    if (war.getName() === "1st Gallic War") return Gallic1
    if (war.getName() === "1st Macedonian War") return Macedonian1
    if (war.getName() === "2nd Macedonian War") return Macedonian2
    if (war.getName() === "1st Illyrian War") return Illyrain1
    if (war.getName() === "2nd Illyrian War") return Illyrain2
    if (war.getName() === "Syrian War") return Syrian
    return Illyrain1
  }

  const getWarStatusCircle = (war: War) => {
    switch (war.status) {
      case "inactive":
        return <div className="h-[16px] w-[16px] bg-green-500 rounded-full"></div>
      case "imminent":
        return <div className="h-[16px] w-[16px] bg-amber-500 rounded-full"></div>
      case "active":
      case "unprosecuted":
        return <div className="h-[16px] w-[16px] bg-red-500 rounded-full"></div>
      case "defeated":
        return <div className="h-[16px] w-[16px] bg-gray-400 rounded-full"></div>
    }
  }


  return (
    <div>
      <div className="p-0.5 bg-black rounded">
        <div className="relative p-0.5 bg-red-600 dark:bg-red-800 flex">
          <div className="absolute bg-black/75 h-[36px] w-[36px] flex justify-center items-center">
            <Image src={MilitaryIcon} alt="War Icon" height={30} width={30} />
          </div>
          <div className="absolute right-0.5 bottom-0.5 h-[36px] w-[36px] flex justify-center items-center">
            <div className="h-[26px] w-[26px] bg-black/75 rounded-full flex justify-center items-center">
              {getWarStatusCircle(war)}
            </div>
          </div>
          <Image
            src={getImage()}
            alt={`Portrait of the ${war.getName()}`}
            height={120}
            width={120}
            placeholder="blur"
            unoptimized
          />
        </div>
      </div>
    </div>
  )
}

export default WarPortrait
