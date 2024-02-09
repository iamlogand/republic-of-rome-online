import Image from "next/image"
import Punic1 from "@/images/wars/punic1.png"
import MilitaryIcon from "@/images/icons/military.svg"
import War from "@/classes/War"

interface WarPortraitProps {
  war: War
}

const WarPortrait = ({ war }: WarPortraitProps) => {
  return (
    <div>
      <div className="p-0.5 bg-black rounded">
        <div className="relative p-0.5 bg-red-600 dark:bg-red-800 flex">
          <div className="absolute rounded-tl bg-black/75 h-[36px] w-[36px] flex justify-center items-center">
            <Image src={MilitaryIcon} alt="War Icon" height={30} width={30} />
          </div>
          <div className="absolute right-0.5 bottom-0.5 h-[36px] w-[36px] flex justify-center items-center">
            <div className="h-[26px] w-[26px] bg-black/75 rounded-full flex justify-center items-center">
              <div className="h-[16px] w-[16px] bg-green-500 rounded-full"></div>
            </div>
          </div>
          <Image
            src={Punic1}
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
