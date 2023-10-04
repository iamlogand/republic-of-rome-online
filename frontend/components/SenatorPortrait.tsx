import { useEffect, useState } from "react"
import Image, { StaticImageData } from "next/image"
import chroma from "chroma-js"

import Senator from "@/classes/Senator"
import Faction from "@/classes/Faction"
import styles from "./SenatorPortrait.module.css"
import Title from "@/classes/Title"
import TitleIcon from "@/components/TitleIcon"
import SelectedDetail from "@/types/selectedDetail"
import Colors from "@/data/colors.json"
import FactionLeaderPattern from "@/images/patterns/factionLeader.svg"
import DeadIcon from "@/images/icons/dead.svg"
import { useGameContext } from "@/contexts/GameContext"
import Collection from "@/classes/Collection"
import { Tooltip } from "@mui/material"

import Cornelius from "@/images/portraits/cornelius.png"
import Fabius from "@/images/portraits/fabius.png"
import Valerius from "@/images/portraits/valerius.png"
import Julius from "@/images/portraits/julius.png"
import Claudius from "@/images/portraits/claudius.png"
import Manlius from "@/images/portraits/manlius.png"
import Fulvius from "@/images/portraits/fulvius.png"
import Furius from "@/images/portraits/furius.png"
import Aurelius from "@/images/portraits/aurelius.png"
import Junius from "@/images/portraits/junius.png"
import Papirius from "@/images/portraits/papirius.png"
import Acilius from "@/images/portraits/acilius.png"
import Flaminius from "@/images/portraits/flaminius.png"
import Aelius from "@/images/portraits/aelius.png"
import Sulpicius from "@/images/portraits/sulpicius.png"
import Calpurnius from "@/images/portraits/calpurnius.png"
import Plautius from "@/images/portraits/plautius.png"
import Quinctius from "@/images/portraits/quinctius.png"
import Aemilius from "@/images/portraits/aemilius.png"
import Terentius from "@/images/portraits/terentius.png"

// Map of senator names to images
const senatorImages: { [key: string]: StaticImageData } = {
  Cornelius: Cornelius,
  Fabius: Fabius,
  Valerius: Valerius,
  Julius: Julius,
  Claudius: Claudius,
  Manlius: Manlius,
  Fulvius: Fulvius,
  Furius: Furius,
  Aurelius: Aurelius,
  Junius: Junius,
  Papirius: Papirius,
  Acilius: Acilius,
  Flaminius: Flaminius,
  Aelius: Aelius,
  Sulpicius: Sulpicius,
  Calpurnius: Calpurnius,
  Plautius: Plautius,
  Quinctius: Quinctius,
  Aemilius: Aemilius,
  Terentius: Terentius,
}

interface SenatorPortraitProps {
  senator: Senator
  size: number
  selectable?: boolean
  nameTooltip?: boolean
}

// The senator portrait is a visual representation of the senator,
// containing an image of their face, faction color background, and other status icons
const SenatorPortrait = ({ senator, size, ...props }: SenatorPortraitProps) => {
  const { allFactions, allTitles, setSelectedDetail } = useGameContext()

  // Used to force a re-render when senator changes
  const [key, setKey] = useState(0)
  useEffect(() => {
    setKey((currentKey) => currentKey + 1)
  }, [senator, setKey])

  // Get senator-specific data
  const faction: Faction | null = senator.faction
    ? allFactions.byId[senator.faction] ?? null
    : null
  const titles: Collection<Title> = new Collection<Title>(
    allTitles.asArray.filter((t) => t.senator === senator.id)
  )
  const majorOffice: Title | null =
    titles.asArray.find((t) => t.major_office === true) ?? null
  const factionLeader: boolean = titles.asArray.some(
    (t) => t.name === "Faction Leader"
  )

  // Used to track whether the mouse is hovering over the portrait
  const [hover, setHover] = useState<boolean>(false)

  // Get style for the image container
  const getImageContainerStyle = () => {
    let bgColor = Colors.dead.primary
    if (faction) {
      bgColor = faction.getColor()
    } else if (senator.alive) {
      bgColor = Colors.unaligned.primary
    }

    return {
      border: "2px solid" + bgColor,
      height: size - 8,
      width: size - 8,
    }
  }

  // Use the name to get the correct image
  const getPicture = (): StaticImageData | string => {
    const senatorName = senator.name
    if (senatorImages.hasOwnProperty(senatorName)) {
      return senatorImages[senatorName]
    } else {
      return ""
    }
  }

  // Get style for the background square
  const getBgStyle = () => {
    // Get base background color
    let bgColor = ""
    if (faction) {
      if (hover) {
        bgColor = faction.getColor("bgHover") // Brighter on hover
      } else {
        bgColor = faction.getColor("bg")
      }
    } else if (senator.alive) {
      if (hover) {
        bgColor = Colors.unaligned.bgHover // Brighter on hover
      } else {
        bgColor = Colors.unaligned.bg
      }
    } else {
      if (hover) {
        bgColor = Colors.dead.bgHover // Brighter on hover
      } else {
        bgColor = Colors.dead.bg
      }
    }

    // Manipulate color to make gradient background
    let innerBgColor = chroma(bgColor).brighten().hex()
    let outerBgColor = chroma(bgColor).darken().hex()

    // Return background style
    return {
      background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")",
      height: size - 6,
      width: size - 6,
    }
  }

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

  // Get the size of the title icon in pixels
  const getIconSize = () => {
    let iconSize = 60
    if (size < 80) {
      iconSize = 28
    } else if (size < 200) {
      iconSize = (32 / 120) * (size - 80) + 28 // linear relationship
    }
    return iconSize
  }

  // Handle mouse interactions
  const handleMouseOver = () => {
    if (props.selectable) setHover(true)
  }
  const handleMouseLeave = () => {
    setHover(false)
  }
  const handleClick = () => {
    if (props.selectable)
      setSelectedDetail({ type: "Senator", id: senator.id } as SelectedDetail)
  }

  // Get JSX for the portrait
  const PortraitElement = props.selectable ? "button" : "div"
  const getPortrait = () => {
    return (
      <PortraitElement
        className={`${styles.senatorPortrait} ${
          props.selectable ? styles.selectable : ""
        }`}
        onMouseOver={handleMouseOver}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        key={key}
      >
        <figure style={{ height: size, width: size }}>
          <div
            className={styles.imageContainer}
            style={getImageContainerStyle()}
          >
            {factionLeader && (
              <Image
                src={FactionLeaderPattern}
                className={styles.factionLeaderPattern}
                alt="Faction Leader pattern"
              />
            )}
            <Image
              className={`${styles.picture} ${
                senator.alive ? "" : styles.dead
              }`}
              width={size + getZoom()}
              height={size + getZoom()}
              src={getPicture()}
              alt={"Portrait of " + senator.displayName}
              style={{ transform: `translate(-50%, -${50 - getOffset()}%)` }}
              placeholder="blur"
            />
          </div>
          <div className={styles.bg} style={getBgStyle()}></div>
          {size > 120 && (
            <Tooltip title="Senator ID" enterDelay={500} arrow>
              <div className={styles.code}># {senator.code}</div>
            </Tooltip>
          )}
          {majorOffice && (
            <TitleIcon title={majorOffice} size={getIconSize()} />
          )}
          {senator.alive === false && (
            <Image
              src={DeadIcon}
              alt="Skull and crossbones icon"
              height={getIconSize()}
              width={getIconSize()}
              className={styles.deadIcon}
            />
          )}
        </figure>
      </PortraitElement>
    )
  }

  if (props.nameTooltip) {
    return (
      <Tooltip
        key={key}
        title={`${senator.displayName}`}
        enterDelay={500}
        arrow
      >
        {getPortrait()}
      </Tooltip>
    )
  } else {
    return getPortrait()
  }
}

export default SenatorPortrait
