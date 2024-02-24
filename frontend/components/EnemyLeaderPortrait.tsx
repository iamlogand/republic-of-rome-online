import EnemyLeader from "@/classes/EnemyLeader"
import Image from "next/image"
import { useAuthContext } from "@/contexts/AuthContext"

import AntiochusIII from "@/images/enemyLeaders/antiochusIII.png"
import Hamilcar from "@/images/enemyLeaders/hamilcar.png"
import Hannibal from "@/images/enemyLeaders/hannibal.png"
import PhilipV from "@/images/enemyLeaders/philipV.png"
import { Tooltip } from "@mui/material"

interface EnemyLeaderPortraitProps {
  enemyLeader: EnemyLeader
  size: number
  nameTooltip?: boolean
}

const EnemyLeaderPortrait = ({
  enemyLeader,
  size,
  nameTooltip,
}: EnemyLeaderPortraitProps) => {
  const { darkMode } = useAuthContext()

  // Get number of pixels by which to increase image size, beyond container size
  const getZoom = () => {
    let zoom = 0
    if (size < 80) {
      zoom = 20
    } else if (size < 200) {
      zoom = (200 - size) / 4 // linear relationship
    }
    return zoom
  }

  // Get number of pixels by which to offset image downwards when zooming in, to focus on the face
  const getOffset = () => {
    let offset = 0
    if (size < 80) {
      offset = 10
    } else if (size < 200) {
      offset = (200 - size) / 12 // linear relationship
    }
    return offset
  }

  const getImageSource = () => {
    switch (enemyLeader.name) {
      case "Antiochus III":
        return AntiochusIII
      case "Hamilcar":
        return Hamilcar
      case "Hannibal":
        return Hannibal
      case "Philip V":
        return PhilipV
    }
    return AntiochusIII // fallback
  }

  const getPortrait = () => (
    <div>
      <figure
        style={{ height: size, width: size }}
        className="ms-0 me-0 m-0 p-0.5 box-border relative flex justify-center items-center bg-stone-700 dark:bg-black select-none rounded shadow"
      >
        <div
          className="absolute overflow-hidden left-1/2 top-1/2 translate-x-[-50%] translate-y-[-50%] border-2 border-solid border-red-600 dark:border-red-700 rounded-[2px]"
          style={{
            background: darkMode
              ? "radial-gradient(hsl(0 25% 70%), hsl(0 25% 35%))"
              : "radial-gradient(hsl(0 100% 97%), hsl(0 30% 66%))",
            height: size - 8,
            width: size - 8,
          }}
        >
          <Image
            width={size + getZoom()}
            height={size + getZoom()}
            src={getImageSource()}
            alt="Portrait of enemy leader"
            placeholder="blur"
            unoptimized
            className="absolute left-1/2 top-1/2"
            style={{ transform: `translate(-50%, -${50 - getOffset()}%)` }}
          />
        </div>
      </figure>
    </div>
  )

  if (nameTooltip) {
    return (
      <Tooltip title={enemyLeader.name} enterDelay={500} arrow>
        {getPortrait()}
      </Tooltip>
    )
  } else {
    return getPortrait()
  }
}

export default EnemyLeaderPortrait
